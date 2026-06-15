from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import func

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
    province = request.args.get('provincia')
    municipality = request.args.get('municipio')
    id_parking = request.args.get('id')
    from_date = request.args.get('fechaDesde')
    to_date = request.args.get('fechaHasta')
    
    # 3. Capturamos los booleanos (Flask los recibe como string, hay que convertirlos)
    isactive = request.args.get('isactive', default='true') # Por defecto 'true' para no mostrar parkings caídos
    has_electricity = request.args.get('electricidad')
    has_waste_disposal = request.args.get('residuales')
    has_vip_spots = request.args.get('vip')

    # 4. Aplicamos los filtros dinámicamente si vienen en la petición
    if id_parking:
        query = query.filter(Parking.id == id_parking)

    if province:
        # ilike hace que no importen las mayúsculas/minúsculas
        query = query.filter(Parking.province.ilike(f"%{province}%"))
        
    if municipality:
        query = query.filter(Parking.municipality.ilike(f"%{municipality}%"))
        
    if isactive:
        # Convertimos el string 'true'/'false' a booleano real de Python
        query = query.filter(Parking.isactive == (isactive.lower() == 'true'))
        
    if has_electricity:
        query = query.filter(Parking.has_electricity == (has_electricity.lower() == 'true'))
        
    if has_waste_disposal:
        query = query.filter(Parking.has_waste_disposal == (has_waste_disposal.lower() == 'true'))
        
    if has_vip_spots:
        query = query.filter(Parking.has_vip_spots == (has_vip_spots.lower() == 'true'))

    # 5. Ejecutamos la consulta y formateamos la respuesta
    filtered_parking = query.all()
    print(filtered_parking)
    return jsonify([p.to_dict(from_date=from_date, to_date=to_date) for p in filtered_parking]), 200

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