from flask import Blueprint, jsonify, request
from flask_babel import gettext as _

from database import db
from models.space import Space

space_bp = Blueprint('space_bp', __name__)


@space_bp.route('/api/space', methods=['GET'])
def get_space():
    """
    Obtiene la lista de plazas o una plaza específica por ID.
    ---
    tags:
      - Space
    parameters:
      - name: id
        in: query
        type: integer
        required: false
        description: ID de la plaza opcional para filtrar un registro específico.
      - name: lang
        in: query
        type: string
        required: false
        description: Idioma para la internacionalización de las respuestas (ej. es, en, eu).
    responses:
      200:
        description: Éxito. Devuelve el objeto estructurado de la plaza o el listado completo.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 42
              name:
                type: string
                example: "Plaza A-12"
              price:
                type: number
                example: 15.50
              id_parking:
                type: integer
                example: 1
      404:
        description: La plaza especificada no existe.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Plaza no existe"
    """
    id = request.args.get('id')

    if id:
        parking = Space.query.get(id)
        if parking:
            return jsonify(parking.to_dict()), 200
        return jsonify({"error": _("Plaza no existe")}), 404

    all = Space.query.all()
    return jsonify([u.to_dict() for u in all]), 200