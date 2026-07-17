import base64
import os
import re
from datetime import date, datetime, timezone
import cv2
import numpy as np
# Importante añadir 'render_template'
from flask import Blueprint, request, jsonify, render_template, current_app
from models.booking import Booking


access_bp = Blueprint('access_bp', __name__)
_reader = None


def _require_access_api_key(fn):
    """Decorador simple para proteger el endpoint de acceso con API key."""
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        configured_key = os.getenv('PUBLIC_API_KEY')
        if not configured_key:
            return jsonify({"error": "Access API is disabled"}), 503
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        if not api_key or api_key != configured_key:
            return jsonify({"error": "Invalid API key"}), 401
        return fn(*args, **kwargs)
    return wrapper


def _get_reader():
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(['es', 'en'], gpu=False)
    return _reader

def clean_plate_text(text):
    return re.sub(r'[\s\-_.]', '', text).upper()

# ==========================================
# 🗺️ VISTA WEB: Muestra la pantalla del Lector
# ==========================================
access_bp
@access_bp.route('/access-control', methods=['GET'])
def access_control_page():
    # Flask busca automáticamente este archivo dentro de la carpeta /templates
    return render_template('access_control.html')


# ==========================================
# 🧠 API: Procesa la foto enviada por la Web
# ==========================================
@access_bp.route('/api/access/verify-plate', methods=['POST'])
@_require_access_api_key
def verify_plate():
    data = request.get_json(silent=True)
    if not data or 'image' not in data:
        return jsonify({"error": "No image data"}), 400

    raw = data['image']
    # El frontend envía data URI "data:image/...;base64,....". Aceptamos también
    # el base64 puro. Validamos el separador para no romper con IndexError.
    if ',' in raw:
        header, _, image_data = raw.partition(',')
        if not header.lower().startswith('data:image'):
            return jsonify({"error": "Formato de imagen no soportado"}), 400
    else:
        image_data = raw

    # Límite de tamaño para evitar DoS por imágenes enormes (CWE-400).
    MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MiB
    if len(image_data) > MAX_IMAGE_BYTES:
        return jsonify({"error": "Imagen demasiado grande"}), 413

    try:
        image_bytes = base64.b64decode(image_data, validate=True)
    except Exception:
        return jsonify({"error": "Datos de imagen inválidos (no es base64)"}), 400

    if len(image_bytes) > MAX_IMAGE_BYTES:
        return jsonify({"error": "Imagen demasiado grande"}), 413

    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        # cv2.imdecode devuelve None si los datos no son una imagen válida.
        if img is None:
            return jsonify({"error": "No se pudo decodificar la imagen"}), 400

        # OpenCV optimización básica
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)

        # Pasar OCR
        results = _get_reader().readtext(gray)
        detected_plate = ""
        for (bbox, text, prob) in results:
            cleaned = clean_plate_text(text)
            if re.match(r'^[A-Z0-9]{3,15}$', cleaned):
                detected_plate = cleaned
                break

        if not detected_plate:
            return jsonify({"access": False, "plate": None, "message": "No se distingue la matrícula clara"}), 200

        # Validar en DB
        today = datetime.now(timezone.utc).date()
        active_booking = Booking.query.filter(
            Booking.license_plate == detected_plate,
            Booking.start_date <= today,
            Booking.end_date >= today,
            Booking.status == '1'
        ).first()

        if active_booking:
            return jsonify({"access": True, "plate": detected_plate, "message": "Barrera abierta"}), 200
        else:
            return jsonify({"access": False, "plate": detected_plate, "message": "Sin reserva activa hoy"}), 200

    except Exception as e:
        current_app.logger.error(f"Error LPR: {str(e)}")
        return jsonify({"error": "Error interno procesando la imagen"}), 500
