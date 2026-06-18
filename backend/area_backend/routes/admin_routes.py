from datetime import date

from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash

from database import db
from models.company import Company
from models.parking import Parking
from models.space import Space
from models.users import Profiles, UserRole, Users
from utils.admin_auth import require_admin, require_super_admin

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/api/admin')


def _parking_to_admin_dict(parking: Parking) -> dict:
    data = parking.to_dict()
    spaces = data.get("spaces", [])
    return {
        **data,
        "localidad": data.get("municipality"),
        "numeroPlazas": len(spaces),
        "tomaElectricidad": data.get("has_electricity"),
        "limpiezaAguasResiduales": data.get("has_waste_disposal"),
        "plazasVip": data.get("has_vip_spots"),
        "isActive": data.get("active"),
        "plazasResponse": spaces,
        "contact_person": parking.contact_person,
    }


def _space_to_admin_dict(space: Space) -> dict:
    data = space.to_dict()
    return {
        **data,
        "nombre": data.get("name"),
        "precio": data.get("price"),
        "estado": data.get("status"),
        "esVip": data.get("isVip"),
        "tieneElectricidad": data.get("hasElectr"),
    }


def _map_parking_fields(data: dict) -> dict:
    return {
        "name": data.get("nombreParking"),
        "province": data.get("provinciaParking"),
        "municipality": data.get("municipioParking"),
        "web_parking": data.get("webParking"),
        "telephone": data.get("telefonoParking"),
        "email": data.get("emailParking"),
        "contact_person": data.get("personaContactoParking"),
        "isactive": data.get("isActivoParking", True),
        "has_electricity": data.get("tieneElectricidadParking", False),
        "has_waste_disposal": data.get("tieneResidualesParking", False),
        "has_vip_spots": data.get("tienePlazasVipParking", False),
    }


def _map_space_fields(data: dict) -> dict:
    return {
        "name": data.get("nombre"),
        "price": data.get("precio"),
        "status": data.get("estado", "0"),
        "isvip": data.get("esVip", False),
        "has_electr": data.get("tieneElectricidad", False),
    }


def _parking_query_for_profile(profile: Profiles):
    query = Parking.query
    if profile.role == UserRole.ADMIN:
        if not profile.company_id:
            return query.filter(False)
        query = query.filter(Parking.id_company == profile.company_id)
    return query


def _can_manage_parking(profile: Profiles, parking: Parking) -> bool:
    if profile.role == UserRole.SUPER_ADMIN:
        return True
    return profile.role == UserRole.ADMIN and profile.company_id == parking.id_company


@admin_bp.route('/parking', methods=['GET'])
@require_admin
def list_parkings(_user, profile):
    parkings = _parking_query_for_profile(profile).all()
    return jsonify([_parking_to_admin_dict(p) for p in parkings]), 200


@admin_bp.route('/parking/space/<int:spot_id>', methods=['GET'])
@require_admin
def get_spot(_user, profile, spot_id):
    space = Space.query.get(spot_id)
    if not space or not space.parking:
        return jsonify({"error": "Plaza no encontrada"}), 404
    if not _can_manage_parking(profile, space.parking):
        return jsonify({"error": "No autorizado"}), 403
    return jsonify(_space_to_admin_dict(space)), 200


@admin_bp.route('/parking/<int:parking_id>', methods=['GET'])
@require_admin
def get_parking(_user, profile, parking_id):
    parking = Parking.query.get(parking_id)
    if not parking:
        return jsonify({"error": "Parking no encontrado"}), 404
    if not _can_manage_parking(profile, parking):
        return jsonify({"error": "No autorizado"}), 403
    return jsonify(_parking_to_admin_dict(parking)), 200


@admin_bp.route('/parking', methods=['POST'])
@require_admin
def create_parking(_user, profile):
    data = request.get_json() or {}
    fields = _map_parking_fields(data)

    if not fields.get("name") or not fields.get("municipality") or not fields.get("email"):
        return jsonify({"error": "Nombre, municipio y email son obligatorios"}), 400

    if profile.role == UserRole.ADMIN:
        company_id = profile.company_id
    else:
        company_id = data.get("companyId") or profile.company_id

    if not company_id:
        company = Company.query.first()
        if not company:
            return jsonify({"error": "No hay empresas registradas"}), 400
        company_id = company.id

    parking = Parking(id_company=company_id, **fields)
    db.session.add(parking)
    db.session.commit()
    return jsonify(_parking_to_admin_dict(parking)), 201


@admin_bp.route('/parking', methods=['PUT'])
@require_admin
def update_parking(_user, profile):
    data = request.get_json() or {}
    parking_id = data.get("idParking")
    if not parking_id:
        return jsonify({"error": "idParking es obligatorio"}), 400

    parking = Parking.query.get(parking_id)
    if not parking:
        return jsonify({"error": "Parking no encontrado"}), 404
    if not _can_manage_parking(profile, parking):
        return jsonify({"error": "No autorizado"}), 403

    for key, value in _map_parking_fields(data).items():
        setattr(parking, key, value)

    db.session.commit()
    return jsonify(_parking_to_admin_dict(parking)), 200


@admin_bp.route('/parking/<int:parking_id>/space', methods=['POST'])
@require_admin
def create_spot(_user, profile, parking_id):
    parking = Parking.query.get(parking_id)
    if not parking:
        return jsonify({"error": "Parking no encontrado"}), 404
    if not _can_manage_parking(profile, parking):
        return jsonify({"error": "No autorizado"}), 403

    data = request.get_json() or {}
    fields = _map_space_fields(data)
    if not fields.get("name"):
        return jsonify({"error": "El nombre de la plaza es obligatorio"}), 400

    space = Space(id_parking=parking.id, **fields)
    db.session.add(space)
    db.session.commit()
    return jsonify(_space_to_admin_dict(space)), 201


@admin_bp.route('/parking/<int:parking_id>/space/<int:spot_id>', methods=['PUT'])
@require_admin
def update_spot(_user, profile, parking_id, spot_id):
    parking = Parking.query.get(parking_id)
    if not parking:
        return jsonify({"error": "Parking no encontrado"}), 404
    if not _can_manage_parking(profile, parking):
        return jsonify({"error": "No autorizado"}), 403

    space = Space.query.filter_by(id=spot_id, id_parking=parking_id).first()
    if not space:
        return jsonify({"error": "Plaza no encontrada"}), 404

    for key, value in _map_space_fields(request.get_json() or {}).items():
        setattr(space, key, value)

    db.session.commit()
    return jsonify(_space_to_admin_dict(space)), 200


@admin_bp.route('/companies', methods=['GET'])
@require_super_admin
def list_companies(_user, _profile):
    companies = Company.query.all()
    return jsonify([c.to_dict() for c in companies]), 200


@admin_bp.route('/users', methods=['GET'])
@require_super_admin
def list_users(_user, _profile):
    users = Users.query.all()
    result = []
    for user in users:
        profile = user.profile
        result.append({
            "id": user.id,
            "email": user.email,
            "isVerified": user.is_verified,
            "nombre": profile.name if profile else "",
            "apellidos": profile.last_name if profile else "",
            "dni": profile.dni if profile else "",
            "role": profile.role.value if profile else "user",
            "companyId": profile.company_id if profile else None,
            "companyName": profile.company.name if profile and profile.company else None,
        })
    return jsonify(result), 200


@admin_bp.route('/users', methods=['POST'])
@require_super_admin
def create_user(_user, _profile):
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    role_name = data.get("role", "user")

    if not email or not password:
        return jsonify({"error": "Email y contraseña son obligatorios"}), 400

    if Users.query.filter_by(email=email).first():
        return jsonify({"error": "El email ya está registrado"}), 409

    role_map = {
        "user": UserRole.USER,
        "admin": UserRole.ADMIN,
        "super_admin": UserRole.SUPER_ADMIN,
    }
    role = role_map.get(role_name, UserRole.USER)
    company_id = data.get("companyId")

    if role == UserRole.ADMIN and not company_id:
        return jsonify({"error": "Los admins deben pertenecer a una empresa"}), 400
    if role == UserRole.SUPER_ADMIN:
        company_id = None

    user = Users(
        email=email,
        pass_user=generate_password_hash(password),
        is_verified=True,
    )
    db.session.add(user)
    db.session.flush()

    profile = Profiles(
        user_id=user.id,
        name=data.get("nombre", "Usuario"),
        last_name=data.get("apellidos", ""),
        dni=data.get("dni", ""),
        birth_day=date(1990, 1, 1),
        role=role,
        company_id=company_id,
    )
    db.session.add(profile)
    db.session.commit()

    return jsonify({"mensaje": "Usuario creado correctamente", "id": user.id}), 201


@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@require_super_admin
def update_user_role(_user, _profile, user_id):
    data = request.get_json() or {}
    role_name = data.get("role")
    if role_name not in ("user", "admin"):
        return jsonify({"error": "Rol no válido. Usa user o admin"}), 400

    user = Users.query.get(user_id)
    if not user or not user.profile:
        return jsonify({"error": "Usuario no encontrado"}), 404
    if user.profile.role == UserRole.SUPER_ADMIN:
        return jsonify({"error": "No se puede modificar un superadministrador"}), 403

    role = UserRole.ADMIN if role_name == "admin" else UserRole.USER
    company_id = data.get("companyId")

    if role == UserRole.ADMIN and not company_id:
        return jsonify({"error": "Los admins deben pertenecer a una empresa"}), 400

    user.profile.role = role
    user.profile.company_id = company_id if role == UserRole.ADMIN else None
    db.session.commit()

    return jsonify({"mensaje": "Permisos actualizados correctamente"}), 200
