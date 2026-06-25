from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_babel import gettext as _, refresh

from database import db
from models.company import Company

company_bp = Blueprint('company_bp', __name__)


@company_bp.route('/api/company', methods=['GET'])
def get_companyes():
    """
    Obtener lista de compañías o una compañía por ID
    ---
    tags:
      - Company
    parameters:
      - name: id
        in: query
        type: integer
        required: false
        description: ID único de la compañía para filtrar un registro específico.
      - name: lang
        in: query
        type: string
        required: false
        description: Idioma para la internacionalización de las respuestas (ej. es, en, eu).
    responses:
      200:
        description: Operación exitosa. Devuelve un objeto o un listado de compañías.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              name:
                type: string
                example: "Transcendence Team S.L."
              cif:
                type: string
                example: "B12345678"
              email:
                type: string
                example: "info@transcendence.com"
      404:
        description: Compañía no encontrada.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Usuario no encontrado"
    """
    id = request.args.get('id')

    if id:
        company = Company.query.get(id)
        if company:
            return jsonify(company.to_dict()), 200
        return jsonify({"error": _("Usuario no encontrado")}), 404

    all = Company.query.all()
    return jsonify([u.to_dict() for u in all]), 200