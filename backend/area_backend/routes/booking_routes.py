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
    if booking.fecha_inicio_reserva and booking.fecha_fin_reserva:
        days = (booking.fecha_fin_reserva - booking.fecha_inicio_reserva).days + 1
    
    plaza = booking.Space
    parking_nombre = ""
    plaza_nombre = ""
    precio_plaza = 0
    if plaza:
        plaza_nombre = plaza.name or ""
        precio_plaza = plaza.precio_plaza or 0
        parking = plaza.parking
        if parking:
            parking_nombre = parking.name or ""
            
    precio_total = days * precio_plaza
    
    return {
        "id": booking.id,
        "fecAlta": booking.fecha_alta_reserva.strftime('%Y-%m-%d') if booking.fecha_alta_reserva else None,
        "fecInicio": booking.fecha_inicio_reserva.isoformat() if booking.fecha_inicio_reserva else None,
        "fecFin": booking.fecha_fin_reserva.isoformat() if booking.fecha_fin_reserva else None,
        "parkingNombre": parking_nombre,
        "estado": booking.estado_reserva,
        "plazaNombre": plaza_nombre,
        "precioTotal": float(precio_total),
        "qrData": f"Reserva #{booking.id} - Plaza {plaza_nombre} en {parking_nombre}"
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

@booking_bp.route('/api/reserva/<int:id>', methods=['GET'])
@jwt_required()
def get_reserva_by_id(id):
    user_id = get_jwt_identity()
    booking = Booking.query.get(id)
    if not booking:
        return jsonify({"error": "Reserva no encontrada"}), 404
        
    if str(booking.id_user) != str(user_id):
        return jsonify({"error": "No tienes permiso para ver esta reserva"}), 403
        
    return jsonify(_get_booking_details(booking)), 200

@booking_bp.route('/api/historico/listado', methods=['GET'])
@jwt_required()
def get_history():
    user_id = get_jwt_identity()
    from models.users import Users
    
    bookings = Booking.query.filter_by(id_user=user_id).all()
    user = Users.query.get(user_id)
    user_email = user.email if user else ""
    
    history = []
    for b in bookings:
        plaza = b.Space
        parking_nombre = ""
        parking_id = 0
        precio = 0
        if plaza:
            precio = plaza.precio_plaza or 0
            parking = plaza.parking
            if parking:
                parking_nombre = parking.name or ""
                parking_id = parking.id
        
        days = 1
        if b.fecha_inicio_reserva and b.fecha_fin_reserva:
            days = (b.fecha_fin_reserva - b.fecha_inicio_reserva).days + 1
        precio_total = days * precio
        
        history.append({
            "id": b.id,
            "usuarioId": int(user_id),
            "usuarioEmail": user_email,
            "plazaId": b.id_space,
            "parkingId": parking_id,
            "parkingNombre": parking_nombre,
            "precio": float(precio),
            "precioTotal": float(precio_total),
            "fecInicio": b.fecha_inicio_reserva.isoformat() if b.fecha_inicio_reserva else None,
            "fecFin": b.fecha_fin_reserva.isoformat() if b.fecha_fin_reserva else None,
            "fecAlta": b.fecha_alta_reserva.strftime('%Y-%m-%d %H:%M:%S') if b.fecha_alta_reserva else None,
            "estado": b.estado_reserva,
            "puntuacion": float(b.puntuacion_reserva) if b.puntuacion_reserva is not None else None
        })
    return jsonify(history), 200

@booking_bp.route('/api/reserva', methods=['POST'])
@jwt_required()
def create_booking():
    user_id = get_jwt_identity()
    data = request.get_json()
    if not data:
        return "Petición inválida", 400
        
    id_plaza = data.get("idPlaza")
    id_parking = data.get("idParking")
    fec_inicio_str = data.get("fecInicio")
    fec_fin_str = data.get("fecFin")
    
    if not id_plaza or not fec_inicio_str or not fec_fin_str:
        return "Faltan campos obligatorios", 400
        
    try:
        fec_inicio = datetime.strptime(fec_inicio_str, "%Y-%m-%d").date()
        fec_fin = datetime.strptime(fec_fin_str, "%Y-%m-%d").date()
    except ValueError:
        return "Formato de fecha inválido", 400
        
    # Validar solapamiento de plaza
    overlap = Booking.query.filter(
        Booking.id_space == id_plaza,
        Booking.fecha_inicio_reserva <= fec_fin,
        Booking.fecha_fin_reserva >= fec_inicio,
        Booking.estado_reserva == "1" # Solo solapa con reservas activas/confirmadas
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
        id_space=id_plaza,
        fecha_inicio_reserva=fec_inicio,
        fecha_fin_reserva=fec_fin,
        estado_reserva="1" # 1 = Confirmada
    )
    db.session.add(new_booking)
    db.session.commit()
    
    return str(new_booking.id), 200

@booking_bp.route('/api/reserva/cancelar', methods=['PUT'])
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

@booking_bp.route('/api/reserva/puntuar', methods=['PUT'])
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

@booking_bp.route('/api/reserva/qr', methods=['POST'])
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