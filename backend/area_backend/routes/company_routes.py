from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from database import db
from models.company import Company

company_bp = Blueprint('company_bp', __name__)


@company_bp.route('/api/company', methods=['GET'])
def get_companyes():
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
        company = Company.query.get(id)
        if company:
            return jsonify(company.to_dict()), 200
        return jsonify({"error": "Usuario no encontrado"}), 404

    all = Company.query.all()
    return jsonify([u.to_dict() for u in all]), 200