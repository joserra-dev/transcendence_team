# pyrefly: ignore [missing-import]
from flask import Blueprint, jsonify, request
# pyrefly: ignore [missing-import]
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_babel import gettext as _ 
from datetime import datetime, date
import os

from database import db
from models.booking import Booking
from models.users import Users
from models.space import Space
from models.parking import Parking
from models.parking_blocked_day import ParkingBlockedDay
from services.email_services import EmailService

booking_bp = Blueprint('booking_bp', __name__)


def clean_license_plate(license_plate):
    if not license_plate:
        return ""
    return str(license_plate).replace(" ", "").replace("-", "").replace("_", "").replace(".", "").upper()


def _get_booking_details(booking):
    days = 0
    if booking.start_date and booking.end_date:
        days = max((booking.end_date - booking.start_date).days, 0)
    
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
        "startDate": booking.start_date.isoformat() if booking.start_date else None,
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
    """
    Obtener reservas del usuario autenticado
    ---
    tags:
      - Booking
    security:
      - Bearer: []
    parameters:
      - name: id
        in: query
        type: integer
        required: false
        description: ID de una reserva específica para filtrar
      - name: lang
        in: query
        type: string
        required: false
        description: Idioma para la internacionalización de las respuestas (ej. es, en, eu)
    responses:
      200:
        description: Lista de reservas o detalle de una reserva específica
      403:
        description: No tienes permiso para ver esta reserva
      404:
        description: Reserva no encontrada
    """
    user_id = get_jwt_identity()
    booking_id = request.args.get('id')

    if booking_id:
        booking = Booking.query.get(booking_id)
        if not booking:
            return jsonify({"error": _("Reserva no encontrada")}), 404
            
        if str(booking.id_user) != str(user_id):
            return jsonify({"error": _("No tienes permiso para ver esta reserva")}), 403
            
        return jsonify(_get_booking_details(booking)), 200

    user_booking = Booking.query.filter_by(id_user=user_id).all()
    return jsonify([_get_booking_details(r) for r in user_booking]), 200

@booking_bp.route('/api/booking/<int:id>', methods=['GET'])
@jwt_required()
def get_reserva_by_id(id):
    """
    Obtener una reserva por su ID de ruta
    ---
    tags:
      - Booking
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID único de la reserva
      - name: lang
        in: query
        type: string
        required: false
        description: Idioma para la internacionalización de las respuestas (ej. es, en, eu)
    responses:
      200:
        description: Detalle estructural de la reserva consultada
      403:
        description: No tienes permiso para ver esta reserva
      404:
        description: Reserva no encontrada
    """
    user_id = get_jwt_identity()
    booking = Booking.query.get(id)
    if not booking:
        return jsonify({"error": "Reserva no encontrada"}), 404
        
    if str(booking.id_user) != str(user_id):
        return jsonify({"error": _("No tienes permiso para ver esta reserva")}), 403
        
    return jsonify(_get_booking_details(booking)), 200

@booking_bp.route('/api/historic/list', methods=['GET'])
@jwt_required()
def get_history():
    """
    Obtener el historial extendido de reservas del usuario
    ---
    tags:
      - Booking
    security:
      - Bearer: []
    parameters:
      - name: lang
        in: query
        type: string
        required: false
        description: Idioma para la internacionalización de las respuestas (ej. es, en, eu)
    responses:
      200:
        description: Listado histórico con mapeo compatible para el frontend
    """
    user_id = get_jwt_identity()
    from models.users import Users
    
    bookings = Booking.query.filter_by(id_user=user_id).all()
    user = Users.query.get(user_id)
    user_email = user.email if user else ""
    
    history = []
    for b in bookings:
        plaza = b.space 
        
        parking_name = ""
        parking_id = 0
        price = 0
        
        if plaza:
            price = plaza.price or 0
            parking = plaza.parking 
            if parking:
                parking_name = parking.name or ""
                parking_id = parking.id
        
        days = 1
        if b.start_date and b.end_date:
            days = max((b.end_date - b.start_date).days, 0)
        total_price = days * price
        
        history.append({
            "id": b.id,
            "userId": int(user_id),
            "userEmail": user_email,
            "spaceId": b.id_space,
            "parkingId": parking_id,
            "parkingName": parking_name,
            "price": float(price),
            "totalPrice": float(total_price),
            "startDate": b.start_date.isoformat() if b.start_date else None,
            "endDate": b.end_date.isoformat() if b.end_date else None,
            "createDate": b.created_at.strftime('%Y-%m-%d %H:%M:%S') if b.created_at else None,
            "status": b.status,
            "range": float(b.rating) if b.rating is not None else None,
            "licensePlate": b.license_plate
        })
        
    return jsonify(history), 200

@booking_bp.route('/api/booking', methods=['POST'])
@jwt_required()
def create_booking():
    """
    Crear una nueva reserva de plaza de parking
    ---
    tags:
      - Booking
    security:
      - Bearer: []
    parameters:
      - name: lang
        in: query
        type: string
        required: false
        description: Idioma para la internacionalización de las respuestas (ej. es, en, eu)
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - idSpace
            - startDate
            - endDate
            - licensePlate
          properties:
            idSpace:
              type: integer
              example: 42
            idParking:
              type: integer
              example: 1
            startDate:
              type: string
              format: date
              example: "2026-07-01"
            endDate:
              type: string
              format: date
              example: "2026-07-05"
            licensePlate:
              type: string
              example: "1234ABC"
    responses:
      200:
        description: Reserva creada con éxito. Devuelve el ID asignado.
      400:
        description: Faltan campos, formato inválido o solapamiento detectado.
    """
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
        return _("Faltan campos obligatorios"), 400

    if not licensePlate:
        return _("La matrícula del vehículo es obligatoria"), 400
        
    try:
        start_date_str = start_date[:10] if isinstance(start_date, str) else start_date
        end_date_str = end_date[:10] if isinstance(end_date, str) else end_date
        startDate = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        endDate = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        return _("Formato de fecha inválido"), 400

    if endDate <= startDate:
        return jsonify({"error": _("La fecha de salida debe ser al menos un día después de la fecha de entrada.")}), 400
        
    same_vehicle_overlap = Booking.query.filter(
        Booking.license_plate == licensePlate,
        Booking.start_date < endDate,
        Booking.end_date > startDate,
        Booking.status == "1"
    ).first()
    
    if same_vehicle_overlap:
        return jsonify({"error": _("Ya existe una reserva para esta matrícula en las fechas seleccionadas. Usa otra matrícula o cambia las fechas.")}), 400

    space_for_block = Space.query.get(id_space)
    if space_for_block:
        blocked_day = ParkingBlockedDay.query.filter(
            ParkingBlockedDay.id_parking == space_for_block.id_parking,
            ParkingBlockedDay.day >= startDate,
            ParkingBlockedDay.day < endDate,
        ).first()
        if blocked_day:
            return jsonify({"error": _("Estas fechas no están disponibles para reservar.")}), 400

    try:
        space = Space.query.get(id_space)
        total_price = 0.0
        if space:
            days = max((endDate - startDate).days, 0)
            total_price = days * float(space.price or 0)
    except Exception:
        total_price = 0.0

    new_booking = Booking(
        id_user=int(user_id),
        id_space=id_space,
        start_date=startDate,
        end_date=endDate,
        status="1", 
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
            management_url = f"{os.getenv('URL_FRONT', 'https://localhost:4200').rstrip('/')}/client/booking/{new_booking.id}"
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
    """
    Cancelar una reserva existente
    ---
    tags:
      - Booking
    security:
      - Bearer: []
    parameters:
      - name: lang
        in: query
        type: string
        required: false
        description: Idioma para la internacionalización de las respuestas (ej. es, en, eu)
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - idReserva
          properties:
            idReserva:
              type: integer
              example: 105
    responses:
      200:
        description: Reserva cancelada correctamente
      400:
        description: Petición inválida o falta idReserva
      403:
        description: No tienes permiso para cancelar esta reserva
      404:
        description: Reserva no encontrada
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": _("Petición inválida")}), 400
        
    id_reserva = data.get("idReserva")
    if not id_reserva:
        return jsonify({"error": _("Falta idReserva")}), 400
        
    booking = Booking.query.get(id_reserva)
    if not booking:
        return jsonify({"error": _("Reserva no encontrada")}), 404
        
    user_id = get_jwt_identity()
    if str(booking.id_user) != str(user_id):
        return jsonify({"error": _("No tienes permiso para cancelar esta reserva")}), 403

    if booking.start_date and booking.start_date <= date.today():
        return jsonify({"error": _("No se puede cancelar una reserva cuya estancia ya ha comenzado o finalizado")}), 400

    booking.status = "0"
    db.session.commit()
    
    return jsonify({"message": _("Reserva cancelada correctamente")}), 200

@booking_bp.route('/api/booking/rate', methods=['PUT'])
@jwt_required()
def rate_booking():
    """
    Puntuar una reserva finalizada
    ---
    tags:
      - Booking
    security:
      - Bearer: []
    parameters:
      - name: lang
        in: query
        type: string
        required: false
        description: Idioma para la internacionalización de las respuestas (ej. es, en, eu)
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - idReserva
            - puntuacion
          properties:
            idReserva:
              type: integer
              example: 105
            puntuacion:
              type: number
              minimum: 1
              maximum: 5
              example: 4.5
    responses:
      200:
        description: Puntuación guardada correctamente
      400:
        description: Faltan campos obligatorios
      403:
        description: No tienes permiso para puntuar esta reserva
      404:
        description: Reserva no encontrada
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": _("Petición inválida")}), 400
        
    id_reserva = data.get("idReserva")
    puntuacion = data.get("puntuacion")
    
    if not id_reserva or puntuacion is None:
        return jsonify({"error": _("Faltan campos obligatorios")}), 400
        
    booking = Booking.query.get(id_reserva)
    if not booking:
        return jsonify({"error": _("Reserva no encontrada")}), 404
        
    user_id = get_jwt_identity()
    if str(booking.id_user) != str(user_id):
        return jsonify({"error": _("No tienes permiso para puntuar esta reserva")}), 403
        
    booking.rating = puntuacion
    db.session.commit()
    
    return jsonify({"message": _("Puntuación guardada correctamente")}), 200

@booking_bp.route('/api/booking/qr', methods=['POST'])
@jwt_required()
def get_qr_code():
    """
    Obtener el código QR de acceso de una reserva
    ---
    tags:
      - Booking
    security:
      - Bearer: []
    parameters:
      - name: lang
        in: query
        type: string
        required: false
        description: Idioma para la internacionalización de las respuestas (ej. es, en, eu)
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - idReserva
          properties:
            idReserva:
              type: integer
              example: 105
    responses:
      200:
        description: Devuelve la imagen del código QR codificada en Base64
      400:
        description: Petición inválida o falta idReserva
      403:
        description: No tienes permiso para ver el QR de esta reserva
      404:
        description: Reserva no encontrada
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": _("Petición inválida")}), 400
        
    id_reserva = data.get("idReserva")
    if not id_reserva:
        return jsonify({"error": _("Falta idReserva")}), 400
        
    booking = Booking.query.get(id_reserva)
    if not booking:
        return jsonify({"error": _("Reserva no encontrada")}), 404
        
    user_id = get_jwt_identity()
    if str(booking.id_user) != str(user_id):
        return jsonify({"error": _("No tienes permiso para ver el QR de esta reserva")}), 403
        
    qr_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAABkAQMAAABKLMIoAAAABlBMVEUAAAD///+l2Z/dAAAAMklEQVQ4y2P4DwUMg6EGBgYGBkYoGBkYGIEBCgYGBkYoGBmYoGBgYICCYWRgYGBkYGCEBwC04AIPfFk1/QAAAABJRU5ErkJggg=="
    return jsonify({"qrBase64": qr_base64}), 200