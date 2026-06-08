from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from database import db
from models.parking import Parking

parking_bp = Blueprint('parking_bp', __name__)


@parking_bp.route('/api/parking', methods=['GET'])
def get_pakings():
    """
    Obtiene la lista de usuarios o un usuario específico por ID.
    ---
    parameters:
      - name: id
        in: query
        type: integer
        required: false
        description: ID del usuario opcional.
    responses:
      200:
        description: Éxito.
    """
    id = request.args.get('id')

    if id:
        parking = Parking.query.get(id)
        if parking:
            return jsonify(parking.to_dict()), 200
        return jsonify({"error": "Usuario no encontrado"}), 404

    all = Parking.query.all()
    return jsonify([u.to_dict() for u in all]), 200