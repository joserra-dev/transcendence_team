from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import db
from models.company import Company
from models.parking import Parking
from models.space import Space
from models.users import Users, Profiles, UserRole

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/api/admin')


def _get_admin_profile():
    user_id = get_jwt_identity()
    user = Users.query.get(user_id)
    if not user or not user.profile:
        return None, None

    profile = user.profile
    if profile.role.value not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]:
        return None, None

    return user, profile


def _require_admin():
    user, profile = _get_admin_profile()
    if not user or not profile:
        return jsonify({"error": "No tienes permisos de administrador"}), 403
    return user, profile


def _parking_to_frontend_dict(parking):
    return {
        "id": parking.id,
        "id_company": parking.id_company,
        "name": parking.name,
        "municipality": parking.municipality,
        "localidad": parking.municipality,
        "province": parking.province,
        "isActive": parking.isactive,
        "web": parking.web_parking,
        "web_parking": parking.web_parking,
        "telephone": parking.telephone,
        "email": parking.email,
        "description": parking.description,
        "longitude": parking.longitude,
        "latitude": parking.latitude,
        "personaContacto": parking.contact_person,
        "contact_person": parking.contact_person,
        "has_electricity": parking.has_electricity,
        "tomaElectricidad": parking.has_electricity,
        "has_waste_disposal": parking.has_waste_disposal,
        "limpiezaAguasResiduales": parking.has_waste_disposal,
        "has_vip_spots": parking.has_vip_spots,
        "plazasVip": parking.has_vip_spots,
        "numeroPlazas": len(parking.spaces or []),
        "spaces": [space.to_dict() for space in (parking.spaces or [])],
        "plazasResponse": [space.to_dict() for space in (parking.spaces or [])],
        "tbai_serie_facturacion": parking.tbai_serie_facturacion,
    }


def _space_to_frontend_dict(space):
    return {
        "id": space.id,
        "id_parking": space.id_parking,
        "name": space.name,
        "isVip": space.isvip,
        "hasElectr": space.has_electr,
        "status": space.status,
        "price": space.price,
        "parkingName": space.parking.name if space.parking else None,
    }


def _parse_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).lower() in ["true", "1", "yes", "si"]


@admin_bp.route('/parking', methods=['GET'])
@jwt_required()
def get_admin_parkings():
    user, profile = _require_admin()
    if isinstance(user, tuple):
        return user

    query = Parking.query
    if profile.role.value != UserRole.SUPER_ADMIN.value and profile.company_id:
        query = query.filter(Parking.id_company == profile.company_id)

    return jsonify([_parking_to_frontend_dict(parking) for parking in query.order_by(Parking.name).all()]), 200


@admin_bp.route('/parking/<int:parking_id>', methods=['GET'])
@jwt_required()
def get_admin_parking(parking_id):
    user, profile = _require_admin()
    if isinstance(user, tuple):
        return user

    parking = Parking.query.get(parking_id)
    if not parking:
        return jsonify({"error": "Parking no encontrado"}), 404

    if profile.role.value != UserRole.SUPER_ADMIN.value and parking.id_company != profile.company_id:
        return jsonify({"error": "No tienes permiso para gestionar este parking"}), 403

    return jsonify(_parking_to_frontend_dict(parking)), 200


@admin_bp.route('/parking', methods=['POST'])
@jwt_required()
def create_parking():
    user, profile = _require_admin()
    if isinstance(user, tuple):
        return user

    data = request.get_json() or {}
    if profile.role.value != UserRole.SUPER_ADMIN.value and not profile.company_id:
        return jsonify({"error": "El administrador debe pertenecer a una empresa"}), 400

    required = ["nombreParking", "emailParking", "municipioParking"]
    missing = [field for field in required if not data.get(field)]
    if missing:
        return jsonify({"error": f"Faltan campos obligatorios: {', '.join(missing)}"}), 400

    parking = Parking(
        id_company=profile.company_id,
        name=data.get("nombreParking", "").strip(),
        province=data.get("provinciaParking", ""),
        municipality=data.get("municipioParking", "").strip(),
        isactive=_parse_bool(data.get("isActivoParking"), True),
        web_parking=data.get("webParking", ""),
        telephone=data.get("telefonoParking", ""),
        email=data.get("emailParking", "").strip(),
        contact_person=data.get("personaContactoParking", ""),
        has_electricity=_parse_bool(data.get("tieneElectricidadParking"), False),
        has_waste_disposal=_parse_bool(data.get("tieneResidualesParking"), False),
        has_vip_spots=_parse_bool(data.get("tienePlazasVipParking"), False),
        tbai_serie_facturacion=data.get("tbai_serie_facturacion", ""),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        description=data.get("description", ""),
    )

    db.session.add(parking)
    db.session.commit()
    return jsonify(_parking_to_frontend_dict(parking)), 201


@admin_bp.route('/parking/<int:parking_id>', methods=['PUT'])
@jwt_required()
def update_parking(parking_id):
    user, profile = _require_admin()
    if isinstance(user, tuple):
        return user

    parking = Parking.query.get(parking_id)
    if not parking:
        return jsonify({"error": "Parking no encontrado"}), 404

    if profile.role.value != UserRole.SUPER_ADMIN.value and parking.id_company != profile.company_id:
        return jsonify({"error": "No tienes permiso para gestionar este parking"}), 403

    data = request.get_json() or {}
    parking.name = data.get("nombreParking", parking.name)
    parking.province = data.get("provinciaParking", parking.province)
    parking.municipality = data.get("municipioParking", parking.municipality)
    parking.web_parking = data.get("webParking", parking.web_parking)
    parking.telephone = data.get("telefonoParking", parking.telephone)
    parking.email = data.get("emailParking", parking.email)
    parking.contact_person = data.get("personaContactoParking", parking.contact_person)
    parking.description = data.get("description", parking.description)
    parking.latitude = data.get("latitude", parking.latitude)
    parking.longitude = data.get("longitude", parking.longitude)
    parking.tbai_serie_facturacion = data.get("tbai_serie_facturacion", parking.tbai_serie_facturacion)

    if "isActivoParking" in data:
        parking.isactive = _parse_bool(data.get("isActivoParking"), True)
    if "tieneElectricidadParking" in data:
        parking.has_electricity = _parse_bool(data.get("tieneElectricidadParking"), False)
    if "tieneResidualesParking" in data:
        parking.has_waste_disposal = _parse_bool(data.get("tieneResidualesParking"), False)
    if "tienePlazasVipParking" in data:
        parking.has_vip_spots = _parse_bool(data.get("tienePlazasVipParking"), False)

    db.session.commit()
    return jsonify(_parking_to_frontend_dict(parking)), 200


@admin_bp.route('/parking/<int:parking_id>/space', methods=['POST'])
@jwt_required()
def create_space(parking_id):
    user, profile = _require_admin()
    if isinstance(user, tuple):
        return user

    parking = Parking.query.get(parking_id)
    if not parking:
        return jsonify({"error": "Parking no encontrado"}), 404

    if profile.role.value != UserRole.SUPER_ADMIN.value and parking.id_company != profile.company_id:
        return jsonify({"error": "No tienes permiso para gestionar este parking"}), 403

    data = request.get_json() or {}
    if not data.get("nombre"):
        return jsonify({"error": "El nombre de la plaza es obligatorio"}), 400

    space = Space(
        id_parking=parking.id,
        name=data.get("nombre", "").strip(),
        price=float(data.get("precio", 0) or 0),
        status=str(data.get("estado", "0")),
        isvip=_parse_bool(data.get("esVip"), False),
        has_electr=_parse_bool(data.get("tieneElectricidad"), False),
    )

    db.session.add(space)
    db.session.commit()
    return jsonify(_space_to_frontend_dict(space)), 201


@admin_bp.route('/parking/<int:parking_id>/space/<int:space_id>', methods=['PUT'])
@jwt_required()
def update_space(parking_id, space_id):
    user, profile = _require_admin()
    if isinstance(user, tuple):
        return user

    parking = Parking.query.get(parking_id)
    space = Space.query.get(space_id)
    if not parking or not space:
        return jsonify({"error": "Parking o plaza no encontrada"}), 404

    if space.id_parking != parking.id:
        return jsonify({"error": "La plaza no pertenece a este parking"}), 400

    if profile.role.value != UserRole.SUPER_ADMIN.value and parking.id_company != profile.company_id:
        return jsonify({"error": "No tienes permiso para gestionar este parking"}), 403

    data = request.get_json() or {}
    if data.get("nombre"):
        space.name = data.get("nombre").strip()
    if "precio" in data:
        space.price = float(data.get("precio", 0) or 0)
    if "estado" in data:
        space.status = str(data.get("estado", "0"))
    if "esVip" in data:
        space.isvip = _parse_bool(data.get("esVip"), False)
    if "tieneElectricidad" in data:
        space.has_electr = _parse_bool(data.get("tieneElectricidad"), False)

    db.session.commit()
    return jsonify(_space_to_frontend_dict(space)), 200


@admin_bp.route('/parking/space/<int:space_id>', methods=['GET'])
@jwt_required()
def get_space(space_id):
    user, profile = _require_admin()
    if isinstance(user, tuple):
        return user

    space = Space.query.get(space_id)
    if not space:
        return jsonify({"error": "Plaza no encontrada"}), 404

    parking = space.parking
    if not parking:
        return jsonify({"error": "Parking no encontrado"}), 404

    if profile.role.value != UserRole.SUPER_ADMIN.value and parking.id_company != profile.company_id:
        return jsonify({"error": "No tienes permiso para gestionar esta plaza"}), 403

    return jsonify(_space_to_frontend_dict(space)), 200


@admin_bp.route('/parking/<int:parking_id>/space/<int:space_id>', methods=['DELETE'])
@jwt_required()
def delete_space(parking_id, space_id):
    user, profile = _require_admin()
    if isinstance(user, tuple):
        return user

    parking = Parking.query.get(parking_id)
    space = Space.query.get(space_id)
    if not parking or not space:
        return jsonify({"error": "Parking o plaza no encontrada"}), 404

    if space.id_parking != parking.id:
        return jsonify({"error": "La plaza no pertenece a este parking"}), 400

    if profile.role.value != UserRole.SUPER_ADMIN.value and parking.id_company != profile.company_id:
        return jsonify({"error": "No tienes permiso para gestionar este parking"}), 403

    db.session.delete(space)
    db.session.commit()
    return jsonify({"message": "Plaza eliminada correctamente"}), 200
