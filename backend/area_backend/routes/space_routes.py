from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_babel import gettext as _, refresh

from database import db
from models.space import Space

space_bp = Blueprint('space_bp', __name__)


@space_bp.route('/api/space', methods=['GET'])
def get_space():
    """
    Obtiene la lista de plazas o una plaza específica por ID.
    ---
    parameters:
      - name: id
        in: query
        type: integer
        required: false
        description: ID de la plaza opcional.
    responses:
      200:
        description: Éxito.
    """
    id = request.args.get('id')

    if id:
        parking = Space.query.get(id)
        if parking:
            return jsonify(parking.to_dict()), 200
        return jsonify({"error": _("Plaza no existe")}), 404

    all = Space.query.all()
    return jsonify([u.to_dict() for u in all]), 200