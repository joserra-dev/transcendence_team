from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import func

from database import db
from models.parking import Parking

parking_bp = Blueprint('parking_bp', __name__)


def _apply_search_filters(query, filters: dict):
    parking_id = filters.get('id')
    if parking_id:
        query = query.filter(Parking.id == parking_id)

    localidad = filters.get('localidad')
    if localidad:
        query = query.filter(func.lower(Parking.municipio_parking).like(f"%{localidad.lower()}%"))

    provincia = filters.get('provincia')
    if provincia:
        query = query.filter(func.lower(Parking.provincia_parking).like(f"%{provincia.lower()}%"))

    if filters.get('tomaElectricidad'):
        query = query.filter(Parking.tiene_electricidad_parking.is_(True))

    if filters.get('limpiezaAguasResiduales'):
        query = query.filter(Parking.tiene_residuales_parking.is_(True))

    if filters.get('plazasVip'):
        query = query.filter(Parking.tiene_plazas_vip_parking.is_(True))

    return query.filter(Parking.isactive.is_(True))


@parking_bp.route('/api/find', methods=['POST'])
def find_parkings():
    filters = request.get_json() or {}
    parkings = _apply_search_filters(Parking.query, filters).all()
    return jsonify([parking.to_dict() for parking in parkings]), 200


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