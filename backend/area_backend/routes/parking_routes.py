from flask import Blueprint, jsonify, request
from sqlalchemy import func
from flask_babel import gettext as _
from datetime import datetime

from database import db
from models.parking import Parking
from models.space import Space

parking_bp = Blueprint('parking_bp', __name__)


@parking_bp.route('/api/parking/search', methods=['GET'])
def search_parkings():
    """
    Busca y filtra parkings por ubicación y servicios disponibles.
    ---
    tags:
      - Parking
    parameters:
      - name: id
        in: query
        type: integer
        required: false
        description: ID único de un parking para una búsqueda directa.
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
      - name: startDate
        in: query
        type: string
        format: date
        required: false
        description: Fecha de inicio para comprobar disponibilidad (YYYY-MM-DD).
      - name: endDate
        in: query
        type: string
        format: date
        required: false
        description: Fecha de fin para comprobar disponibilidad (YYYY-MM-DD).
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
      - name: lang
        in: query
        type: string
        required: false
        description: Idioma para la internacionalización de las respuestas (ej. es, en, eu).
    responses:
      200:
        description: Lista de parkings filtrados correctamente.
    """
    # Iniciamos la query base sobre el modelo Parking
    query = Parking.query

    # Capturamos los parámetros de texto de la URL
    province = request.args.get('provincia')
    municipality = request.args.get('municipio')
    id_parking = request.args.get('id')
    from_date_str = request.args.get('startDate')
    to_date_str = request.args.get('endDate')
    from_date = None
    to_date = None
    if from_date_str:
        try:
            from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": _("Formato de fecha inválido para startDate. Usa YYYY-MM-DD.")}), 400
    if to_date_str:
        try:
            to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": _("Formato de fecha inválido para endDate. Usa YYYY-MM-DD.")}), 400
    
    # Capturamos los booleanos (Flask los recibe como string, hay que convertirlos)
    isactive = request.args.get('isactive', default='true') # Por defecto 'true' para no mostrar parkings caídos
    has_electricity = request.args.get('electricidad')
    has_waste_disposal = request.args.get('residuales')
    has_vip_spots = request.args.get('vip')

    # Capturamos parámetros de paginación y ordenación
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    sort = request.args.get('sort', 'name')
    order = request.args.get('order', 'asc')

    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 20

    allowed_sorts = {'name', 'municipality', 'province', 'latitude', 'longitude', 'created_at'}
    sort_col = sort if sort in allowed_sorts else 'name'
    order_col = getattr(Parking, sort_col)
    if str(order).lower() == 'desc':
        query = query.order_by(order_col.desc())
    else:
        query = query.order_by(order_col.asc())

    # Aplicamos el resto de filtros
    if id_parking:
        query = query.filter(Parking.id == id_parking, Space.status == '0')

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

    # Ejecutamos la consulta y aplicamos paginación
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    items = [p.to_dict(from_date=from_date, to_date=to_date) for p in pagination.items]

    if id_parking and len(items) == 0:
        return jsonify({"error": "Parking no encontrado"}), 404

    return jsonify({
        "items": items,
        "total": pagination.total,
        "page": page,
        "limit": limit,
        "pages": pagination.pages,
    }), 200

@parking_bp.route('/api/parking', methods=['GET'])
def get_pakings():
    """
    Obtiene la lista de parkings o un parking específico por ID.
    ---
    tags:
      - Parking
    parameters:
      - name: id
        in: query
        type: integer
        required: false
        description: ID del parking opcional.
      - name: lang
        in: query
        type: string
        required: false
        description: Idioma para la internacionalización de las respuestas (ej. es, en, eu).
    responses:
      200:
        description: Éxito. Devuelve el objeto o listado de parkings.
      404:
        description: Parking no encontrado.
    """
    id = request.args.get('id')

    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    sort = request.args.get('sort', 'name')
    order = request.args.get('order', 'asc')

    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 20

    allowed_sorts = {'name', 'municipality', 'province', 'latitude', 'longitude', 'created_at'}
    sort_col = sort if sort in allowed_sorts else 'name'
    order_col = getattr(Parking, sort_col)

    query = Parking.query
    if id:
        query = query.filter(Parking.id == id)
        page = 1
        limit = 1

    if str(order).lower() == 'desc':
        query = query.order_by(order_col.desc())
    else:
        query = query.order_by(order_col.asc())

    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    items = [p.to_dict() for p in pagination.items]

    if id and not items:
        return jsonify({"error": _("Parking no encontrado")}), 404

    if id:
        return jsonify(items[0]), 200

    return jsonify({
        "items": items,
        "total": pagination.total,
        "page": page,
        "limit": limit,
        "pages": pagination.pages,
    }), 200