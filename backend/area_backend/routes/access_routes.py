import base64
import re
from datetime import date, datetime, timezone
import cv2
import numpy as np
# Importante añadir 'render_template'
from flask import Blueprint, request, jsonify, render_template 
from models.booking import Booking


access_bp = Blueprint('access_bp', __name__)
_reader = None


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
def verify_plate():
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({"error": "No image data"}), 400

    try:
        # Decodificar Base64
        image_data = data['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

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
        print(f"Error LPR: {str(e)}")
        return jsonify({"error": "Error interno"}), 500