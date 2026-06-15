# pyrefly: ignore [missing-import]
from flask import Blueprint, jsonify, request
# pyrefly: ignore [missing-import]
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from database import db
from models.booking import Booking

booking_bp = Blueprint('booking_bp', __name__)

def _get_booking_details(booking):
    days = 1
    if booking.start_date and booking.end_date:
        days = (booking.end_date - booking.start_date).days + 1
    
    space = booking.space
    parking_name = ""
    spaceName = ""
    price = 0
    if space:
        spaceName = space.name or ""
        price = space.price or 0
        parking = space.parking
        if parking:
            parking_name = parking.name or ""
            
    total_price = days * price
    
    return {
        "id": booking.id,
        "createDate": booking.created_at.strftime('%Y-%m-%d') if booking.created_at else None,
        "starDate": booking.start_date.isoformat() if booking.start_date else None,
        "endDate": booking.end_date.isoformat() if booking.end_date else None,
        "parkingName": parking_name,
        "status": booking.status,
        "spaceName": spaceName,
        "totalPrice": float(total_price),
        "license_plate":booking.license_plate,
        "qrData": f"Reserva #{booking.id} - Plaza {spaceName} en {parking_name}"
    }

@booking_bp.route('/api/booking', methods=['GET'])
@jwt_required() 
def get_booking():
    user_id = get_jwt_identity()
    booking_id = request.args.get('id')

    if booking_id:
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({"error": "Reserva no encontrada"}), 404
            
        if str(booking.id_user) != str(user_id):
            return jsonify({"error": "No tienes permiso para ver esta reserva"}), 403
            
        return jsonify(_get_booking_details(booking)), 200

    user_booking = Booking.query.filter_by(id_user=user_id).all()
    return jsonify([_get_booking_details(r) for r in user_booking]), 200

@booking_bp.route('/api/booking/<int:id>', methods=['GET'])
@jwt_required()
def get_reserva_by_id(id):
    user_id = get_jwt_identity()
    booking = Booking.query.get(id)
    if not booking:
        return jsonify({"error": "Reserva no encontrada"}), 404
        
    if str(booking.id_user) != str(user_id):
        return jsonify({"error": "No tienes permiso para ver esta reserva"}), 403
        
    return jsonify(_get_booking_details(booking)), 200

@booking_bp.route('/api/historic/list', methods=['GET'])
@jwt_required()
def get_history():
    user_id = get_jwt_identity()
    from models.users import Users
    
    # 1. Traemos las reservas del usuario usando el campo correcto en inglés (id_user)
    bookings = Booking.query.filter_by(id_user=user_id).all()
    user = Users.query.get(user_id)
    user_email = user.email if user else ""
    
    history = []
    for b in bookings:
        # CORRECCIÓN CLAVE: Accedemos directamente a la relación 'space' del modelo Booking
        plaza = b.space 
        
        parking_name = ""
        parking_id = 0
        price = 0
        
        if plaza:
            price = plaza.price or 0
            # Accedemos a la relación 'parking' desde el modelo Space
            parking = plaza.parking 
            if parking:
                parking_name = parking.name or parking.name or ""
                parking_id = parking.id
        
        # 2. Cálculo de días usando los nuevos campos en inglés de Booking (start_date y end_date)
        days = 1
        if b.start_date and b.end_date:
            days = (b.end_date - b.start_date).days + 1
        total_price = days * price
        
        # 3. Mapeo del diccionario. Mantenemos las claves antiguas que Angular espera,
        # pero leyendo las propiedades nuevas de los modelos.
        history.append({
            "id": b.id,
            "userId": int(user_id),
            "userEmail": user_email,
            "spaceId": b.id_space,
            "parkingId": parking_id,
            "parkingName": parking_name,
            "price": float(price),
            "totalPrice": float(total_price),
            # Propiedades de fecha y estado cambiadas a inglés:
            "startDate": b.start_date.isoformat() if b.start_date else None,
            "endDate": b.end_date.isoformat() if b.end_date else None,
            "createDate": b.created_at.strftime('%Y-%m-%d %H:%M:%S') if b.created_at else None,
            "status": b.status,
            "range": float(b.rating) if b.rating is not None else None,
            # NUEVO: Enviamos la matrícula al Frontend para el historial
            "licensePlate": b.license_plate
        })
        
    return jsonify(history), 200

@booking_bp.route('/api/booking', methods=['POST'])
@jwt_required()
def create_booking():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return "Petición inválida", 400
        
    id_space = data.get("idSpace")
    id_parking = data.get("idParking")
    start_date = data.get("startDate")
    end_date = data.get("endDate")
    licensePlate = data.get("licensePlate")
    
    if not id_space or not start_date or not end_date:
        return "Faltan campos obligatorios", 400
        
    try:
        startDate = datetime.strptime(start_date, "%Y-%m-%d").date()
        endDate = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return "Formato de fecha inválido", 400
        
    # Validar solapamiento de plaza
    overlap = Booking.query.filter(
        Booking.id_space == id_space,
        Booking.start_date <= startDate,
        Booking.end_date >= endDate,
        Booking.status == "1" # Solo solapa con reservas activas/confirmadas
    ).first()
    
    if overlap:
        return "La plaza ya está ocupada en las fechas seleccionadas", 400

    # Validar solapamiento de usuario (el usuario ya tiene una reserva en esas fechas en cualquier plaza)
    user_overlap = Booking.query.filter(
        Booking.id_user == int(user_id),
        Booking.fecha_inicio_reserva <= fec_fin,
        Booking.fecha_fin_reserva >= fec_inicio,
        Booking.estado_reserva == "1" # Solo solapa con reservas activas/confirmadas
    ).first()

    if user_overlap:
        return jsonify({"error": "Ya tienes una reserva para ti en estas fechas. No puedes reservar más de una plaza a la vez."}), 400
        
    new_booking = Booking(
        id_user=int(user_id),
        id_space=id_space,
        start_date=startDate,
        end_date=endDate,
        status="1", # 1 = Confirmada
        license_plate=licensePlate.upper()
    )
    db.session.add(new_booking)
    db.session.commit()
    
    return str(new_booking.id), 200

@booking_bp.route('/api/booking/cancel', methods=['PUT'])
@jwt_required()
def cancel_booking():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Petición inválida"}), 400
        
    id_reserva = data.get("idReserva")
    if not id_reserva:
        return jsonify({"error": "Falta idReserva"}), 400
        
    booking = Booking.query.get(id_reserva)
    if not booking:
        return jsonify({"error": "Reserva no encontrada"}), 404
        
    user_id = get_jwt_identity()
    if str(booking.id_user) != str(user_id):
        return jsonify({"error": "No tienes permiso para cancelar esta reserva"}), 403
        
    booking.estado_reserva = "0" # 0 = Cancelada
    db.session.commit()
    
    return jsonify({"message": "Reserva cancelada correctamente"}), 200

@booking_bp.route('/api/booking/rate', methods=['PUT'])
@jwt_required()
def rate_booking():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Petición inválida"}), 400
        
    id_reserva = data.get("idReserva")
    puntuacion = data.get("puntuacion")
    
    if not id_reserva or puntuacion is None:
        return jsonify({"error": "Faltan campos obligatorios"}), 400
        
    booking = Booking.query.get(id_reserva)
    if not booking:
        return jsonify({"error": "Reserva no encontrada"}), 404
        
    user_id = get_jwt_identity()
    if str(booking.id_user) != str(user_id):
        return jsonify({"error": "No tienes permiso para puntuar esta reserva"}), 403
        
    booking.puntuacion_reserva = puntuacion
    db.session.commit()
    
    return jsonify({"message": "Puntuación guardada correctamente"}), 200

@booking_bp.route('/api/booking/qr', methods=['POST'])
@jwt_required()
def get_qr_code():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Petición inválida"}), 400
        
    id_reserva = data.get("idReserva")
    if not id_reserva:
        return jsonify({"error": "Falta idReserva"}), 400
        
    booking = Booking.query.get(id_reserva)
    if not booking:
        return jsonify({"error": "Reserva no encontrada"}), 404
        
    user_id = get_jwt_identity()
    if str(booking.id_user) != str(user_id):
        return jsonify({"error": "No tienes permiso para ver el QR de esta reserva"}), 403
        
    # Generar un código QR en base64 estático pero válido
    # Este es una imagen PNG de un código QR simple
    qr_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAABkAQMAAABKLMIoAAAABlBMVEUAAAD///+l2Z/dAAAAMklEQVQ4y2P4DwUMg6EGBgYGBkYoGBkYGIEBCgYGBkYoGBmYoGBgYICCYWRgYGBkYGCEBwC04AIPfFk1/QAAAABJRU5ErkJggg=="
    return jsonify({"qrBase64": qr_base64}), 200