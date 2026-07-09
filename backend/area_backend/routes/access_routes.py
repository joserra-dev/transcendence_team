import base64
import re
from datetime import date
import cv2
import numpy as np
import easyocr
from flask import Blueprint, request, jsonify, render_template
from models.booking import Booking
from models.space import Space
from models.parking import Parking


access_bp = Blueprint('access_bp', __name__)
reader = easyocr.Reader(['es', 'en'], gpu=False)

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


# Lista de parkings activos
@access_bp.route('/api/access/parkings', methods=['GET'])
def get_parkings():
    parkings = Parking.query.filter_by(isactive=True).all()
    return jsonify([{"id": p.id, "name": p.name} for p in parkings])


# ==========================================
# 🧠 API: Procesa la foto enviada por la Web
# ==========================================
@access_bp.route('/api/access/verify-plate', methods=['POST'])
def verify_plate():
    data = request.get_json()
    if not data or 'image' not in data or 'parking_id' not in data:
        return jsonify({"error": "Falta imagen o parking_id"}), 400

    parking_id = data['parking_id']

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
        results = reader.readtext(gray)
        detected_plate = ""
        for (bbox, text, prob) in results:
            cleaned = clean_plate_text(text)
            if re.match(r'^[A-Z0-9]{3,15}$', cleaned):
                detected_plate = cleaned
                break

        if not detected_plate:
            return jsonify({"access": False, "plate": None, "message": "No se distingue la matrícula clara"}), 200

        # Validar en DB
        today = date.today()
        active_booking = Booking.query.join(Space).filter(
            Booking.license_plate == detected_plate,
            Booking.start_date <= today,
            Booking.end_date >= today,
            Booking.status == '1',
            Space.id_parking == parking_id
        ).first()

        if active_booking:
            return jsonify({"access": True, "plate": detected_plate, "message": "Barrera abierta"}), 200
        else:
            return jsonify({"access": False, "plate": detected_plate, "message": "Sin reserva activa hoy"}), 200

    except Exception as e:
        print(f"Error LPR: {str(e)}")
        return jsonify({"error": "Error interno"}), 500