# pyrefly: ignore [missing-import]
from flask import Blueprint, jsonify, request
# pyrefly: ignore [missing-import]
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import os

from database import db
from models.booking import Booking
from models.users import Users
from models.space import Space
from models.parking import Parking
from services.email_services import EmailService
from utils.pdf_generator import PdfGenerator

booking_bp = Blueprint('booking_bp', __name__)


def clean_license_plate(license_plate):
    if not license_plate:
        return ""
    return str(license_plate).replace(" ", "").replace("-", "").replace("_", "").replace(".", "").upper()


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
        "license_plate": booking.license_plate,
        "licensePlate": booking.license_plate,
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
    licensePlate = clean_license_plate(data.get("licensePlate"))
    
    if not id_space or not start_date or not end_date:
        return "Faltan campos obligatorios", 400

    if not licensePlate:
        return "La matrícula del vehículo es obligatoria", 400
        
    try:
        startDate = datetime.strptime(start_date, "%Y-%m-%d").date()
        endDate = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return "Formato de fecha inválido", 400

    if endDate <= startDate:
        return jsonify({"error": "La fecha de salida debe ser al menos un día después de la fecha de entrada."}), 400
        
    # Validar solapamiento de plaza
    # Permitimos reservas coincidentes en la misma plaza si la matrícula es diferente.
    # Solo bloqueamos duplicados de la misma matrícula en fechas solapadas.
    same_vehicle_overlap = Booking.query.filter(
        Booking.license_plate == licensePlate,
        Booking.start_date <= endDate,
        Booking.end_date >= startDate,
        Booking.status == "1"
    ).first()
    
    if same_vehicle_overlap:
        return jsonify({"error": "Ya existe una reserva para esta matrícula en las fechas seleccionadas. Usa otra matrícula o cambia las fechas."}), 400
        
    try:
        from models.space import Space
        space = Space.query.get(id_space)
        total_price = 0.0
        if space:
            days = max((endDate - startDate).days + 1, 0)
            total_price = days * float(space.price or 0)
    except Exception:
        total_price = 0.0

    new_booking = Booking(
        id_user=int(user_id),
        id_space=id_space,
        start_date=startDate,
        end_date=endDate,
        status="1", # 1 = Confirmada
        license_plate=licensePlate.upper() if licensePlate else "",
        total_price=total_price
    )
    db.session.add(new_booking)
    db.session.commit()

    try:
        user = Users.query.get(new_booking.id_user)
        space = Space.query.get(new_booking.id_space)
        parking = space.parking if space else None
        if user and parking:
            management_url = f"{os.getenv('URL_FRONT', 'http://localhost:4200').rstrip('/')}/client/booking/{new_booking.id}"
            EmailService.booking(
                destinatario=user.email,
                user_name=user.profile.name if user.profile else user.email,
                booking_code=str(new_booking.id),
                service_detail=f"{parking.name} - {space.name if space else ''}",
                booking_date=f"{new_booking.start_date} a {new_booking.end_date}",
                total_paid=f"{new_booking.total_price:.2f}€",
                management_url=management_url
            )
    except Exception as exc:
        db.session.rollback()
        print(f"Error enviando correo de reserva: {exc}")

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
        
    booking.status = "0" # 0 = Cancelada
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

@booking_bp.route('/api/booking/<int:id>/bill', methods=['GET'])
@jwt_required()
def get_bill_by_id(id):
    user_id = get_jwt_identity()
    #booking = Booking.query.get(id)
    booking = Booking.query.filter_by(id=id, id_user=user_id).first()
    print (booking)
    #print (booking.space.id_parking) 
    parking = Parking.query.filter_by(id=booking.space.id_parking).first()
    user_email = Users.query.get(user_id).email
    #print (parking.name)   
    if not booking:
        return jsonify({"error": "Reserva no encontrada"}), 404
        
    if str(booking.id_user) != str(user_id):
        return jsonify({"error": "No tienes permiso para ver esta reserva"}), 403

    # TODO: llamar a la funcion PDF_GENERATOR()

    bill = PdfGenerator.pdf_generator(booking, parking)

    
    #TODO: llamar a la funcion para mandar el email
    EmailService.send_bill(user_email, bill)
    
    
    return jsonify({"OK": "Email con factura enviado"}), 200