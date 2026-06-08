from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from database import db
from models.booking import Booking

booking_bp = Blueprint('booking_bp', __name__)


@booking_bp.route('/api/booking', methods=['GET'])
@jwt_required() 
def get_booking():
    """
    Obtiene las reservas del usuario autenticado. Puede filtrar una reserva específica por ID.
    ---
    tags:
      - Reservas
    security:
      - BearerAuth: []
    parameters:
      - name: id
        in: query
        type: integer
        required: false
        description: ID de una reserva específica (opcional).
    responses:
      200:
        description: Lista de reservas del usuario o una reserva específica.
      403:
        description: No tienes permisos para ver esta reserva.
      404:
        description: Reserva no encontrada.
    """
    # 1. Obtenemos el ID del usuario logueado desde el token JWT
    user_id = get_jwt_identity()
    booking_id = request.args.get('id')

    # Caso A: Si pasan un ID por la URL (/api/booking?id=5)
    if booking_id:
        booking = Booking.query.get(booking_id)
        
        if not booking:
            return jsonify({"error": "Reserva no encontrada"}), 404
            
        # ⚠️ SEGURIDAD: Verificamos que la reserva realmente le pertenezca al usuario del JWT
        # Ajusta 'reserva.user_id' según cómo se llame el campo en tu modelo Booking
        if str(booking.user_id) != str(user_id):
            return jsonify({"error": "No tienes permiso para ver esta reserva"}), 403
            
        return jsonify(booking.to_dict()), 200

    # Caso B: Si no pasan ID, devolvemos TODAS las reservas de ESTE usuario
    # Ajusta 'user_id' al nombre exacto de la clave foránea en tu modelo Booking
    user_booking = Booking.query.filter_by(user_id=user_id).all()
    
    return jsonify([r.to_dict() for r in user_booking]), 200