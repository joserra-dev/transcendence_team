from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from database import db
from models.parking import Parking

parking_bp = Blueprint('parking_bp', __name__)


@parking_bp.route('/api/parking/search', methods=['GET'])
def search_parkings():
    """
    Busca y filtra parkings por ubicación y servicios disponibles.
    ---
    parameters:
      - name: provincia
        in: query
        type: string
        required: false
        description: Filtrar por provincia.
      - name: municipio
        in: query
        type: string
        required: false
        description: Filtrar por municipio.
      - name: isactive
        in: query
        type: boolean
        required: false
        description: Filtrar por estado activo (true/false). Por defecto busca los activos.
      - name: electricidad
        in: query
        type: boolean
        required: false
        description: Filtrar si tiene electricidad (true/false).
      - name: residuales
        in: query
        type: boolean
        required: false
        description: Filtrar si tiene vaciado de residuales (true/false).
      - name: vip
        in: query
        type: boolean
        required: false
        description: Filtrar si tiene plazas VIP (true/false).
    responses:
      200:
        description: Lista de parkings filtrados correctamente.
    """
    # 1. Iniciamos la query base sobre el modelo Parking
    query = Parking.query

    # 2. Capturamos los parámetros de texto de la URL
    provincia = request.args.get('provincia')
    municipio = request.args.get('municipio')
    
    # 3. Capturamos los booleanos (Flask los recibe como string, hay que convertirlos)
    isactive = request.args.get('isactive', default='true') # Por defecto 'true' para no mostrar parkings caídos
    tiene_electricidad = request.args.get('electricidad')
    tiene_residuales = request.args.get('residuales')
    tiene_vip = request.args.get('vip')

    # 4. Aplicamos los filtros dinámicamente si vienen en la petición
    if provincia:
        # ilike hace que no importen las mayúsculas/minúsculas
        query = query.filter(Parking.provincia_parking.ilike(f"%{provincia}%"))
        
    if municipio:
        query = query.filter(Parking.municipio_parking.ilike(f"%{municipio}%"))
        
    if isactive:
        # Convertimos el string 'true'/'false' a booleano real de Python
        query = query.filter(Parking.isactive == (isactive.lower() == 'true'))
        
    if tiene_electricidad:
        query = query.filter(Parking.tiene_electricidad_parking == (tiene_electricidad.lower() == 'true'))
        
    if tiene_residuales:
        query = query.filter(Parking.tiene_residuales_parking == (tiene_residuales.lower() == 'true'))
        
    if tiene_vip:
        query = query.filter(Parking.tiene_plazas_vip_parking == (tiene_vip.lower() == 'true'))

    # 5. Ejecutamos la consulta y formateamos la respuesta
    parkings_filtrados = query.all()
    
    return jsonify([p.to_dict() for p in parkings_filtrados]), 200

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