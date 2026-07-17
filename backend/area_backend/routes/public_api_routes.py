import os
from functools import wraps
from datetime import datetime, date

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from database import db, limiter
from models.booking import Booking
from models.parking import Parking
from models.space import Space
from models.users import Users

public_api_bp = Blueprint('public_api_bp', __name__, url_prefix='/api/public')

RATE_LIMIT_PER_MINUTE = int(os.getenv('PUBLIC_API_RATE_LIMIT', '60'))

# NOTA: Con Flask-Limiter + Redis (RATELIMIT_STORAGE_URI) este límite es
# compartido entre todos los workers/contenedores y sí protege en producción.


def _require_public_api_key(fn):
    @wraps(fn)
    @limiter.limit(f"{RATE_LIMIT_PER_MINUTE} per minute")
    def wrapper(*args, **kwargs):
        configured_key = os.getenv('PUBLIC_API_KEY')
        if not configured_key:
            return jsonify({"error": "Public API is disabled"}), 503

        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        if not api_key or api_key != configured_key:
            return jsonify({"error": "Invalid API key"}), 401

        return fn(*args, **kwargs)
    return wrapper


def _parking_summary(parking):
    return {
        "id": parking.id,
        "name": parking.name,
        "municipality": parking.municipality,
        "province": parking.province,
        "has_electricity": parking.has_electricity,
        "has_waste_disposal": parking.has_waste_disposal,
        "has_vip_spots": parking.has_vip_spots,
        "latitude": parking.latitude,
        "longitude": parking.longitude,
        "spots_count": len(parking.spaces or []),
    }


def _space_payload(space):
    return {
        "id": space.id,
        "name": space.name,
        "is_vip": space.isvip,
        "has_electricity": space.has_electr,
        "status": space.status,
        "price": space.price,
        "parking_id": space.id_parking,
    }


@public_api_bp.route('/parkings', methods=['GET'])
@_require_public_api_key
def list_parkings():
    """Public API: list parkings with optional filters and pagination."""
    query = Parking.query.filter(Parking.isactive.is_(True))
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')

    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 20

    allowed_sorts = {'id', 'name', 'municipality', 'province', 'latitude', 'longitude'}
    sort_col = sort if sort in allowed_sorts else 'id'
    order_col = getattr(Parking, sort_col)

    province = request.args.get('province')
    municipality = request.args.get('municipality')
    if province:
        query = query.filter(Parking.province.ilike(f"%{province}%"))
    if municipality:
        query = query.filter(Parking.municipality.ilike(f"%{municipality}%"))

    if str(order).lower() == 'desc':
        query = query.order_by(order_col.desc())
    else:
        query = query.order_by(order_col.asc())

    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    return jsonify({
        "items": [_parking_summary(parking) for parking in pagination.items],
        "total": pagination.total,
        "page": page,
        "limit": limit,
        "pages": pagination.pages,
    }), 200


@public_api_bp.route('/parkings/search', methods=['POST'])
@_require_public_api_key
def search_parkings():
    """Public API: search parkings by dates and amenities with pagination."""
    data = request.get_json() or {}
    query = Parking.query.filter(Parking.isactive.is_(True))

    page = int(data.get('page') or 1)
    limit = int(data.get('limit') or 20)
    sort = data.get('sort', 'id')
    order = data.get('order', 'asc')

    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 20

    allowed_sorts = {'id', 'name', 'municipality', 'province', 'latitude', 'longitude'}
    sort_col = sort if sort in allowed_sorts else 'id'
    order_col = getattr(Parking, sort_col)

    if data.get('province'):
        query = query.filter(Parking.province.ilike(f"%{data['province']}%"))
    if data.get('municipality'):
        query = query.filter(Parking.municipality.ilike(f"%{data['municipality']}%"))
    if data.get('electricity') is not None:
        query = query.filter(Parking.has_electricity.is_(bool(data['electricity'])))
    if data.get('waste_disposal') is not None:
        query = query.filter(Parking.has_waste_disposal.is_(bool(data['waste_disposal'])))
    if data.get('vip_spots') is not None:
        query = query.filter(Parking.has_vip_spots.is_(bool(data['vip_spots'])))

    if str(order).lower() == 'desc':
        query = query.order_by(order_col.desc())
    else:
        query = query.order_by(order_col.asc())

    from_date = data.get('startDate')
    to_date = data.get('endDate')
    from_date_obj = None
    to_date_obj = None
    if from_date:
        try:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido. Usa YYYY-MM-DD."}), 400
    if to_date:
        try:
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido. Usa YYYY-MM-DD."}), 400
    parkings = []
    for parking in query.all():
        parking_data = _parking_summary(parking)
        if from_date_obj and to_date_obj:
            parking_data['available_spots'] = [
                _space_payload(space) for space in parking.spaces or []
                if not Booking.query.filter(
                    Booking.id_space == space.id,
                    Booking.start_date < to_date_obj,
                    Booking.end_date > from_date_obj,
                    Booking.status == '1'
                ).first()
            ]
        else:
            parking_data['available_spots'] = [_space_payload(space) for space in (parking.spaces or [])]
        parkings.append(parking_data)

    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paged_items = parkings[start_idx:end_idx]

    return jsonify({
        "items": paged_items,
        "total": len(parkings),
        "page": page,
        "limit": limit,
        "pages": (len(parkings) + limit - 1) // limit,
    }), 200


@public_api_bp.route('/parkings/<int:parking_id>', methods=['GET'])
@_require_public_api_key
def get_parking(parking_id):
    """Public API: get one parking by id."""
    parking = Parking.query.get(parking_id)
    if not parking:
        return jsonify({"error": "Parking not found"}), 404
    return jsonify(_parking_summary(parking)), 200


@public_api_bp.route('/spaces/<int:space_id>/status', methods=['PUT'])
@_require_public_api_key
def update_space_status(space_id):
    """Public API: update maintenance/free status for a space."""
    data = request.get_json() or {}
    space = Space.query.get(space_id)
    if not space:
        return jsonify({"error": "Space not found"}), 404

    status = str(data.get('status', space.status or '0'))
    if status not in ['0', '1', '2']:
        return jsonify({"error": "Invalid status"}), 400

    space.status = status
    db.session.commit()
    return jsonify(_space_payload(space)), 200


@public_api_bp.route('/spaces/<int:space_id>', methods=['DELETE'])
@_require_public_api_key
def delete_space(space_id):
    """Public API: delete a space."""
    space = Space.query.get(space_id)
    if not space:
        return jsonify({"error": "Space not found"}), 404

    db.session.delete(space)
    db.session.commit()
    return jsonify({"message": "Space deleted"}), 200
