from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_babel import gettext as _, refresh

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
        return jsonify({"error": _("No tienes permisos de administrador")}), 403
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
    """
    Listar parkings autorizados para el administrador
    ---
    tags:
      - Admin Parking
    security:
      - Bearer: []
    parameters:
      - name: lang
        in: query
        type: string
        required: false
        description: Idioma para la internacionalización de las respuestas (ej. es, en, eu).
    responses:
      200:
        description: Listado de parkings disponibles bajo el alcance del administrador.
      403:
        description: No tienes permisos de administrador.
    """
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
    """
    Obtener el detalle administrativo de un parking específico
    ---
    tags:
      - Admin Parking
    security:
      - Bearer: []
    parameters:
      - name: parking_id
        in: path
        type: integer
        required: true
        description: ID único del parking a consultar.
      - name: lang
        in: query
        type: string
        required: false
        description: Idioma para la internacionalización de las respuestas.
    responses:
      200:
        description: Información detallada del parking.
      403:
        description: No tienes permisos de gestión sobre este parking.
      404:
        description: Parking no encontrado.
    """
    user, profile = _require_admin()
    if isinstance(user, tuple):
        return user

    parking = Parking.query.get(parking_id)
    if not parking:
        return jsonify({"error": _("Parking no encontrado")}), 404

    if profile.role.value != UserRole.SUPER_ADMIN.value and parking.id_company != profile.company_id:
        return jsonify({"error": _("No tienes permiso para gestionar este parking")}), 403

    return jsonify(_parking_to_frontend_dict(parking)), 200


@admin_bp.route('/parking', methods=['POST'])
@jwt_required()
def create_parking():
    """
    Dar de alta un nuevo parking
    ---
    tags:
      - Admin Parking
    security:
      - Bearer: []
    parameters:
      - name: lang
        in: query
        type: string
        required: false
        description: Idioma para la internacionalización de las respuestas.
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - nombreParking
            - emailParking
            - municipioParking
          properties:
            nombreParking:
              type: string
              example: "Parking Central"
            emailParking:
              type: string
              example: "central@parking.com"
            municipioParking:
              type: string
              example: "Donostia"
            provinciaParking:
              type: string
              example: "Gipuzkoa"
            isActivoParking:
              type: boolean
              example: true
            webParking:
              type: string
              example: "https://parkingcentral.com"
            telefonoParking:
              type: string
              example: "943000000"
            personaContactoParking:
              type: string
              example: "Ion Anai"
            tieneElectricidadParking:
              type: boolean
              example: true
            tieneResidualesParking:
              type: boolean
              example: false
            tienePlazasVipParking:
              type: boolean
              example: true
            tbai_serie_facturacion:
              type: string
              example: "A"
            latitude:
              type: number
              example: 43.3183
            longitude:
              type: number
              example: -1.9812
            description:
              type: string
              example: "Parking vigilado 24 horas en el centro."
    responses:
      201:
        description: Parking creado correctamente con el alcance corporativo asignado.
      400:
        description: Faltan campos obligatorios o el administrador carece de asignación empresarial.
      403:
        description: No tienes permisos de administrador.
    """
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
    """
    Modificar las propiedades de un parking existente
    ---
    tags:
      - Admin Parking
    security:
      - Bearer: []
    parameters:
      - name: parking_id
        in: path
        type: integer
        required: true
        description: ID del parking a actualizar.
      - name: lang
        in: query
        type: string
        required: false
        description: Idioma para la internacionalización de las respuestas.
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            nombreParking:
              type: string
            provinciaParking:
              type: string
            municipioParking:
              type: string
            webParking:
              type: string
            telefonoParking:
              type: string
            emailParking:
              type: string
            personaContactoParking:
              type: string
            description:
              type: string
            latitude:
              type: number
            longitude:
              type: number
            tbai_serie_facturacion:
              type: string
            isActivoParking:
              type: boolean
            tieneElectricidadParking:
              type: boolean
            tieneResidualesParking:
              type: boolean
            tienePlazasVipParking:
              type: boolean
    responses:
      200:
        description: Parking actualizado correctamente.
      403:
        description: Permisos denegados sobre este recurso.
      404:
        description: Parking no encontrado.
    """
    user, profile = _require_admin()
    if isinstance(user, tuple):
        return user

    parking = Parking.query.get(parking_id)
    if not parking:
        return jsonify({"error": _("Parking no encontrado")}), 404

    if profile.role.value != UserRole.SUPER_ADMIN.value and parking.id_company != profile.company_id:
        return jsonify({"error": _("No tienes permiso para gestionar este parking")}), 403

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
    """
    Crear una nueva plaza dentro de un parking autorizado
    ---
    tags:
      - Admin Space
    security:
      - Bearer: []
    parameters:
      - name: parking_id
        in: path
        type: integer
        required: true
        description: ID del parking dueño de la plaza.
      - name: lang
        in: query
        type: string
        required: false
        description: Idioma para la internacionalización de las respuestas.
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - nombre
          properties:
            nombre:
              type: string
              example: "Plaza VIP 01"
            precio:
              type: number
              example: 22.50
            estado:
              type: string
              example: "1"
            esVip:
              type: boolean
              example: true
            tieneElectricidad:
              type: boolean
              example: true
    responses:
      201:
        description: Plaza creada exitosamente.
      400:
        description: El nombre de la plaza es obligatorio.
      403:
        description: Privilegios insuficientes sobre el recurso parking.
      404:
        description: Parking no encontrado.
    """
    user, profile = _require_admin()
    if isinstance(user, tuple):
        return user

    parking = Parking.query.get(parking_id)
    if not parking:
        return jsonify({"error": _("Parking no encontrado")}), 404

    if profile.role.value != UserRole.SUPER_ADMIN.value and parking.id_company != profile.company_id:
        return jsonify({"error": _("No tienes permiso para gestionar este parking")}), 403

    data = request.get_json() or {}
    if not data.get("nombre"):
        return jsonify({"error": _("El nombre de la plaza es obligatorio")}), 400

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
    """
    Modificar una plaza de parking específica
    ---
    tags:
      - Admin Space
    security:
      - Bearer: []
    parameters:
      - name: parking_id
        in: path
        type: integer
        required: true
        description: ID del parking asignado.
      - name: space_id
        in: path
        type: integer
        required: true
        description: ID único de la plaza a cambiar.
      - name: lang
        in: query
        type: string
        required: false
        description: Idioma para la internacionalización de las respuestas.
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            nombre:
              type: string
            precio:
              type: number
            estado:
              type: string
            esVip:
              type: boolean
            tieneElectricidad:
              type: boolean
    responses:
      200:
        description: Plaza editada correctamente.
      400:
        description: Incoherencia en los identificadores de la plaza y el parking.
      403:
        description: Permisos corporativos insuficientes.
      404:
        description: Recursos no encontrados.
    """
    user, profile = _require_admin()
    if isinstance(user, tuple):
        return user

    parking = Parking.query.get(parking_id)
    space = Space.query.get(space_id)
    if not parking or not space:
        return jsonify({"error": _("Parking o plaza no encontrada")}), 404

    if space.id_parking != parking.id:
        return jsonify({"error": _("La plaza no pertenece a este parking")}), 400

    if profile.role.value != UserRole.SUPER_ADMIN.value and parking.id_company != profile.company_id:
        return jsonify({"error": _("No tienes permiso para gestionar este parking")}), 403

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
    """
    Consultar los datos estructurales de una plaza de parking individual
    ---
    tags:
      - Admin Space
    security:
      - Bearer: []
    parameters:
      - name: space_id
        in: path
        type: integer
        required: true
        description: ID único de la plaza.
      - name: lang
        in: query
        type: string
        required: false
        description: Idioma para la internacionalización de las respuestas.
    responses:
      200:
        description: Datos detallados de la plaza de parking.
      403:
        description: No posees permisos para interactuar con esta plaza.
      404:
        description: Plaza o parking asociado inexistente.
    """
    user, profile = _require_admin()
    if isinstance(user, tuple):
        return user

    space = Space.query.get(space_id)
    if not space:
        return jsonify({"error": _("Plaza no encontrada")}), 404

    parking = space.parking
    if not parking:
        return jsonify({"error": _("Parking no encontrado")}), 404

    if profile.role.value != UserRole.SUPER_ADMIN.value and parking.id_company != profile.company_id:
        return jsonify({"error": _("No tienes permiso para gestionar esta plaza")}), 403

    return jsonify(_space_to_frontend_dict(space)), 200


@admin_bp.route('/parking/<int:parking_id>/space/<int:space_id>', methods=['DELETE'])
@jwt_required()
def delete_space(parking_id, space_id):
    """
    Eliminar de manera permanente una plaza de parking
    ---
    tags:
      - Admin Space
    security:
      - Bearer: []
    parameters:
      - name: parking_id
        in: path
        type: integer
        required: true
        description: ID del parking titular.
      - name: space_id
        in: path
        type: integer
        required: true
        description: ID de la plaza a suprimir.
      - name: lang
        in: query
        type: string
        required: false
        description: Idioma para la internacionalización de las respuestas.
    responses:
      200:
        description: Mensaje confirmando la eliminación.
      400:
        description: Conflicto de pertenencia entre la plaza y el parking.
      403:
        description: El administrador no tiene asignados permisos corporativos para esta supresión.
      404:
        description: Estructuras no encontradas en la base de datos.
    """
    user, profile = _require_admin()
    if isinstance(user, tuple):
        return user

    parking = Parking.query.get(parking_id)
    space = Space.query.get(space_id)
    if not parking or not space:
        return jsonify({"error": _("Parking o plaza no encontrada")}), 404

    if space.id_parking != parking.id:
        return jsonify({"error": _("La plaza no pertenece a este parking")}), 400

    if profile.role.value != UserRole.SUPER_ADMIN.value and parking.id_company != profile.company_id:
        return jsonify({"error": _("No tienes permiso para gestionar este parking")}), 403

    db.session.delete(space)
    db.session.commit()
    return jsonify({"message": _("Plaza eliminada correctamente")}), 200