from datetime import date
import secrets

from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash
from flask_babel import gettext as _

from database import db
from models.booking import Booking
from models.company import Company
from models.parking import Parking
from models.space import Space
from models.users import Profiles, UserRole, Users
from services.email_services import EmailService
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


def _booking_query_for_profile(profile: Profiles):
    query = Booking.query.join(Space).join(Parking)
    if profile.role == UserRole.ADMIN:
        if not profile.company_id:
            return query.filter(False)
        query = query.filter(Parking.id_company == profile.company_id)
    return query


def _can_manage_booking(profile: Profiles, booking: Booking) -> bool:
    space = booking.space
    if not space or not space.parking:
        return False
    return _can_manage_parking(profile, space.parking)


def _booking_to_admin_dict(booking: Booking) -> dict:
    days = 0
    if booking.start_date and booking.end_date:
        days = max((booking.end_date - booking.start_date).days, 0)

    space = booking.space
    parking_name = ""
    parking_id = 0
    space_name = ""
    price = 0.0
    if space:
        space_name = space.name or ""
        price = float(space.price or 0)
        parking = space.parking
        if parking:
            parking_name = parking.name or ""
            parking_id = parking.id

    total_price = float(booking.total_price) if booking.total_price else days * price
    user = booking.user
    user_email = user.email if user else ""
    user_name = ""
    if user and user.profile:
        user_name = f"{user.profile.name or ''} {user.profile.last_name or ''}".strip()

    return {
        "id": booking.id,
        "userId": booking.id_user,
        "userEmail": user_email,
        "userName": user_name,
        "spaceId": booking.id_space,
        "spaceName": space_name,
        "parkingId": parking_id,
        "parkingName": parking_name,
        "price": price,
        "totalPrice": total_price,
        "startDate": booking.start_date.isoformat() if booking.start_date else None,
        "endDate": booking.end_date.isoformat() if booking.end_date else None,
        "createDate": booking.created_at.strftime('%Y-%m-%d %H:%M:%S') if booking.created_at else None,
        "status": booking.status,
        "rating": float(booking.rating) if booking.rating is not None else None,
        "licensePlate": booking.license_plate,
    }


def _user_to_admin_dict(user: Users) -> dict:
    profile = user.profile
    return {
        "id": user.id,
        "email": user.email,
        "isVerified": user.is_verified,
        "nombre": profile.name if profile else "",
        "apellidos": profile.last_name if profile else "",
        "dni": profile.dni if profile else "",
        "role": profile.role.value if profile else "user",
        "companyId": profile.company_id if profile else None,
        "companyName": profile.company.name if profile and profile.company else None,
    }


def _create_pending_user(email: str, password: str) -> tuple[Users, str]:
    verification_token = secrets.token_urlsafe(32)
    user = Users(
        email=email,
        pass_user=generate_password_hash(password),
        is_verified=False,
        verification_token=verification_token,
    )
    return user, verification_token


def _company_to_admin_dict(company: Company) -> dict:
    data = company.to_dict()
    data["parkingCount"] = len(company.parkings)
    admin_profile = Profiles.query.filter_by(
        company_id=company.id, role=UserRole.ADMIN
    ).first()
    if admin_profile and admin_profile.user:
        data["adminUserId"] = admin_profile.user.id
        data["adminEmail"] = admin_profile.user.email
        data["adminName"] = admin_profile.name
        data["adminApellidos"] = admin_profile.last_name
        data["adminDni"] = admin_profile.dni
    else:
        data["adminUserId"] = None
        data["adminEmail"] = None
        data["adminName"] = None
        data["adminApellidos"] = None
        data["adminDni"] = None
    return data


@admin_bp.route('/parking', methods=['GET'])
@require_admin
def list_parkings(_user, profile):
    """
    Listar parkings administrables
    ---
    tags:
      - Admin Parking
    security:
      - Bearer: []
    parameters:
      - name: companyId
        in: query
        type: integer
        required: false
        description: ID de la empresa para filtrar (solo Super Admin)
      - name: lang
        in: query
        type: string
        required: false
        description: Idioma para la internacionalización (ej. es, en, eu)
    responses:
      200:
        description: Listado de parkings devuelto correctamente.
    """
    query = _parking_query_for_profile(profile)
    company_id = request.args.get('companyId', type=int)
    if company_id and profile.role == UserRole.SUPER_ADMIN:
        query = query.filter(Parking.id_company == company_id)
    parkings = query.all()
    return jsonify([_parking_to_admin_dict(p) for p in parkings]), 200


@admin_bp.route('/parking/space/<int:spot_id>', methods=['GET'])
@require_admin
def get_spot(_user, profile, spot_id):
    """
    Obtener detalles de una plaza específica
    ---
    tags:
      - Admin Parking
    security:
      - Bearer: []
    parameters:
      - name: spot_id
        in: path
        type: integer
        required: true
        description: ID único de la plaza
      - name: lang
        in: query
        type: string
        required: false
        description: Idioma para la internacionalización
    responses:
      200:
        description: Detalles estructurales de la plaza
      403:
        description: No autorizado para gestionar este parking
      404:
        description: Plaza no encontrada
    """
    space = Space.query.get(spot_id)
    if not space or not space.parking:
        return jsonify({"error": _("Plaza no encontrada")}), 404
    if not _can_manage_parking(profile, space.parking):
        return jsonify({"error": _("No autorizado")}), 403
    return jsonify(_space_to_admin_dict(space)), 200


@admin_bp.route('/parking/<int:parking_id>', methods=['GET'])
@require_admin
def get_parking(_user, profile, parking_id):
    """
    Obtener detalles de un parking específico
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
        description: ID del parking
      - name: lang
        in: query
        type: string
        required: false
    responses:
      200:
        description: Información detallada del parking
      403:
        description: No autorizado
      404:
        description: Parking no encontrado
    """
    parking = Parking.query.get(parking_id)
    if not parking:
        return jsonify({"error": _("Parking no encontrado")}), 404
    if not _can_manage_parking(profile, parking):
        return jsonify({"error": _("No autorizado")}), 403
    return jsonify(_parking_to_admin_dict(parking)), 200


@admin_bp.route('/parking', methods=['POST'])
@require_admin
def create_parking(_user, profile):
    """
    Crear un nuevo parking
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
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - nombreParking
            - municipioParking
            - emailParking
          properties:
            nombreParking:
              type: string
              example: "Parking Centro"
            provinciaParking:
              type: string
              example: "Madrid"
            municipioParking:
              type: string
              example: "Madrid"
            emailParking:
              type: string
              example: "centro@parking.com"
            companyId:
              type: integer
              example: 1
    responses:
      201:
        description: Parking creado con éxito
      400:
        description: Faltan campos obligatorios o no existen empresas registradas
    """
    data = request.get_json() or {}
    fields = _map_parking_fields(data)

    if not fields.get("name") or not fields.get("municipality") or not fields.get("email"):
        return jsonify({"error": _("Nombre, municipio y email son obligatorios")}), 400

    if profile.role == UserRole.ADMIN:
        company_id = profile.company_id
    else:
        company_id = data.get("companyId") or profile.company_id

    if not company_id:
        company = Company.query.first()
        if not company:
            return jsonify({"error": _("No hay empresas registradas")}), 400
        company_id = company.id

    parking = Parking(id_company=company_id, **fields)
    db.session.add(parking)
    db.session.commit()
    return jsonify(_parking_to_admin_dict(parking)), 201


@admin_bp.route('/parking', methods=['PUT'])
@require_admin
def update_parking(_user, profile):
    """
    Actualizar un parking existente
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
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - idParking
          properties:
            idParking:
              type: integer
              example: 1
            nombreParking:
              type: string
              example: "Parking Centro Actualizado"
    responses:
      200:
        description: Parking modificado con éxito
      400:
        description: ID del parking obligatorio
      403:
        description: No autorizado
      404:
        description: Parking no encontrado
    """
    data = request.get_json() or {}
    parking_id = data.get("idParking")
    if not parking_id:
        return jsonify({"error": _("idParking es obligatorio")}), 400

    parking = Parking.query.get(parking_id)
    if not parking:
        return jsonify({"error": _("Parking no encontrado")}), 404
    if not _can_manage_parking(profile, parking):
        return jsonify({"error": _("No autorizado")}), 403

    for key, value in _map_parking_fields(data).items():
        setattr(parking, key, value)

    db.session.commit()
    return jsonify(_parking_to_admin_dict(parking)), 200


@admin_bp.route('/parking/<int:parking_id>', methods=['DELETE'])
@require_admin
def delete_parking(_user, profile, parking_id):
    """
    Eliminar un parking y sus plazas asociadas
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
    responses:
      200:
        description: Parking eliminado correctamente
      403:
        description: No autorizado
      404:
        description: Parking no encontrado
    """
    parking = Parking.query.get(parking_id)
    if not parking:
        return jsonify({"error": _("Parking no encontrado")}), 404
    if not _can_manage_parking(profile, parking):
        return jsonify({"error": _("No autorizado")}), 403

    for space in list(parking.spaces):
        db.session.delete(space)
    db.session.delete(parking)
    db.session.commit()
    return jsonify({"mensaje": _("Parking eliminado correctamente")}), 200


@admin_bp.route('/parking/<int:parking_id>/space', methods=['POST'])
@require_admin
def create_spot(_user, profile, parking_id):
    """
    Crear una plaza de estacionamiento en un parking
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
              example: "Plaza A-01"
            precio:
              type: number
              example: 12.5
    responses:
      201:
        description: Plaza creada con éxito
      400:
        description: Nombre de plaza obligatorio
      403:
        description: No autorizado
      404:
        description: Parking no encontrado
    """
    parking = Parking.query.get(parking_id)
    if not parking:
        return jsonify({"error": _("Parking no encontrado")}), 404
    if not _can_manage_parking(profile, parking):
        return jsonify({"error": _("No autorizado")}), 403

    data = request.get_json() or {}
    fields = _map_space_fields(data)
    if not fields.get("name"):
        return jsonify({"error": _("El nombre de la plaza es obligatorio")}), 400

    space = Space(id_parking=parking.id, **fields)
    db.session.add(space)
    db.session.commit()
    return jsonify(_space_to_admin_dict(space)), 201


@admin_bp.route('/parking/<int:parking_id>/space/<int:spot_id>', methods=['PUT'])
@require_admin
def update_spot(_user, profile, parking_id, spot_id):
    """
    Actualizar datos de una plaza específica
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
      - name: spot_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
    responses:
      200:
        description: Plaza actualizada correctamente
      403:
        description: No autorizado
      404:
        description: Parking o plaza no encontrada
    """
    parking = Parking.query.get(parking_id)
    if not parking:
        return jsonify({"error": _("Parking no encontrado")}), 404
    if not _can_manage_parking(profile, parking):
        return jsonify({"error": _("No autorizado")}), 403

    space = Space.query.filter_by(id=spot_id, id_parking=parking_id).first()
    if not space:
        return jsonify({"error": _("Plaza no encontrada")}), 404

    for key, value in _map_space_fields(request.get_json() or {}).items():
        setattr(space, key, value)

    db.session.commit()
    return jsonify(_space_to_admin_dict(space)), 200


@admin_bp.route('/bookings', methods=['GET'])
@require_admin
def list_bookings(_user, profile):
    """
    Listar y filtrar reservas (Vista Global/Admin)
    ---
    tags:
      - Admin Bookings
    security:
      - Bearer: []
    parameters:
      - name: parkingId
        in: query
        type: integer
        required: false
      - name: companyId
        in: query
        type: integer
        required: false
      - name: status
        in: query
        type: string
        required: false
    responses:
      200:
        description: Historial de reservas procesadas
    """
    query = _booking_query_for_profile(profile)

    parking_id = request.args.get('parkingId', type=int)
    if parking_id:
        query = query.filter(Parking.id == parking_id)

    company_id = request.args.get('companyId', type=int)
    if company_id and profile.role == UserRole.SUPER_ADMIN:
        query = query.filter(Parking.id_company == company_id)

    status = request.args.get('status')
    if status:
        query = query.filter(Booking.status == status)

    bookings = query.order_by(Booking.created_at.desc()).all()
    return jsonify([_booking_to_admin_dict(b) for b in bookings]), 200


@admin_bp.route('/bookings/<int:booking_id>', methods=['GET'])
@require_admin
def get_booking(_user, profile, booking_id):
    """
    Obtener el detalle de una reserva gestionable
    ---
    tags:
      - Admin Bookings
    security:
      - Bearer: []
    parameters:
      - name: booking_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Esquema de datos de la reserva
      403:
        description: No autorizado
      404:
        description: Reserva no encontrada
    """
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": _("Reserva no encontrada")}), 404
    if not _can_manage_booking(profile, booking):
        return jsonify({"error": _("No autorizado")}), 403
    return jsonify(_booking_to_admin_dict(booking)), 200


@admin_bp.route('/bookings/<int:booking_id>/cancel', methods=['PUT'])
@require_admin
def cancel_booking_admin(_user, profile, booking_id):
    """
    Cancelar administrativamente una reserva
    ---
    tags:
      - Admin Bookings
    security:
      - Bearer: []
    parameters:
      - name: booking_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Reserva cancelada correctamente
      400:
        description: La reserva ya se encuentra cancelada previamente
      403:
        description: No autorizado
      404:
        description: Reserva no encontrada
    """
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": _("Reserva no encontrada")}), 404
    if not _can_manage_booking(profile, booking):
        return jsonify({"error": _("No autorizado")}), 403
    if booking.status == '0':
        return jsonify({"error": _("La reserva ya está cancelada")}), 400

    booking.status = '0'
    db.session.commit()
    return jsonify({"mensaje": _("Reserva cancelada correctamente")}), 200


@admin_bp.route('/companies', methods=['GET'])
@require_super_admin
def list_companies(_user, _profile):
    """
    Listar todas las empresas asignadas (Solo Super Admin)
    ---
    tags:
      - Admin Companies
    security:
      - Bearer: []
    responses:
      200:
        description: Listado de empresas registradas en el sistema
    """
    companies = Company.query.all()
    return jsonify([_company_to_admin_dict(c) for c in companies]), 200


@admin_bp.route('/companies', methods=['POST'])
@require_super_admin
def create_company(_user, _profile):
    """
    Registrar una nueva empresa junto a su administrador principal (Solo Super Admin)
    ---
    tags:
      - Admin Companies
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - adminEmail
            - adminPassword
          properties:
            name:
              type: string
              example: "Parkings S.A."
            cif:
              type: string
              example: "A1234567B"
            adminEmail:
              type: string
              example: "admin@parkingsa.com"
            adminPassword:
              type: string
              example: "segura123"
    responses:
      201:
        description: Empresa y administrador creados, correo de verificación emitido
      400:
        description: Faltan campos obligatorios
      409:
        description: El email del administrador ya está registrado
      500:
        description: Error crítico al enviar el email transaccional
    """
    data = request.get_json() or {}
    name = data.get("name")
    cif = data.get("cif")
    email = data.get("adminEmail")
    password = data.get("adminPassword")
    nombre = data.get("adminNombre", "")
    apellidos = data.get("adminApellidos", "")
    dni = data.get("adminDni", "")

    if not name:
        return jsonify({"error": _("El nombre de la empresa es obligatorio")}), 400
    if not email or not password:
        return jsonify(
            {"error": _("Email y contraseña del administrador son obligatorios")}
        ), 400
    if Users.query.filter_by(email=email).first():
        return jsonify({"error": _("El email ya está registrado")}), 409

    company = Company(name=name, cif=cif or None)
    db.session.add(company)
    db.session.flush()

    user, verification_token = _create_pending_user(email, password)
    db.session.add(user)
    db.session.flush()

    admin_profile = Profiles(
        user_id=user.id,
        name=nombre or "Admin",
        last_name=apellidos or "",
        dni=dni or "",
        birth_day=date(1990, 1, 1),
        role=UserRole.ADMIN,
        company_id=company.id,
    )
    db.session.add(admin_profile)
    try:
        EmailService.welcome(email, verification_token)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": _("Error al enviar el correo de verificación")}), 500

    return jsonify(_company_to_admin_dict(company)), 201


@admin_bp.route('/companies/<int:company_id>', methods=['GET'])
@require_super_admin
def get_company(_user, _profile, company_id):
    """
    Visualizar datos de una empresa (Solo Super Admin)
    ---
    tags:
      - Admin Companies
    security:
      - Bearer: []
    parameters:
      - name: company_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Información de la empresa
      404:
        description: Empresa no encontrada
    """
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"error": _("Empresa no encontrada")}), 404
    return jsonify(_company_to_admin_dict(company)), 200


@admin_bp.route('/companies/<int:company_id>', methods=['PUT'])
@require_super_admin
def update_company(_user, _profile, company_id):
    """
    Actualizar datos básicos de una empresa (Solo Super Admin)
    ---
    tags:
      - Admin Companies
    security:
      - Bearer: []
    parameters:
      - name: company_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
    responses:
      200:
        description: Empresa modificada con éxito
      400:
        description: El nombre de la empresa es obligatorio
      404:
        description: Empresa no encontrada
    """
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"error": _("Empresa no encontrada")}), 404

    data = request.get_json() or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": _("El nombre de la empresa es obligatorio")}), 400

    company.name = name
    if "cif" in data:
        company.cif = data["cif"] or None

    db.session.commit()
    return jsonify(_company_to_admin_dict(company)), 200


@admin_bp.route('/companies/<int:company_id>', methods=['DELETE'])
@require_super_admin
def delete_company(_user, _profile, company_id):
    """
    Eliminar empresa en cascada junto a parkings y plazas (Solo Super Admin)
    ---
    tags:
      - Admin Companies
    security:
      - Bearer: []
    parameters:
      - name: company_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Empresa eliminada correctamente
      404:
        description: Empresa no encontrada
    """
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"error": _("Empresa no encontrada")}), 404

    for parking in list(company.parkings):
        for space in list(parking.spaces):
            db.session.delete(space)
        db.session.delete(parking)

    for profile in Profiles.query.filter_by(company_id=company_id).all():
        profile.company_id = None
        if profile.role == UserRole.ADMIN:
            profile.role = UserRole.USER

    db.session.delete(company)
    db.session.commit()
    return jsonify({"mensaje": _("Empresa eliminada correctamente")}), 200


@admin_bp.route('/companies/<int:company_id>/users', methods=['GET'])
@require_super_admin
def list_company_users(_user, _profile, company_id):
    """
    Listar los usuarios asociados a una empresa (Solo Super Admin)
    ---
    tags:
      - Admin Companies
    security:
      - Bearer: []
    parameters:
      - name: company_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Usuarios pertenecientes a la entidad corporativa
      404:
        description: Empresa no encontrada
    """
    company = Company.query.get(company_id)
    if not company:
        return jsonify({"error": _("Empresa no encontrada")}), 404

    profiles = Profiles.query.filter_by(company_id=company_id).all()
    result = []
    for profile in profiles:
        if profile.user:
            result.append(_user_to_admin_dict(profile.user))
    return jsonify(result), 200


@admin_bp.route('/users', methods=['GET'])
@require_super_admin
def list_users(_user, _profile):
    """
    Listar todos los usuarios globales del ecosistema (Solo Super Admin)
    ---
    tags:
      - Admin Users
    security:
      - Bearer: []
    responses:
      200:
        description: Base total de usuarios
    """
    users = Users.query.all()
    return jsonify([_user_to_admin_dict(user) for user in users]), 200


@admin_bp.route('/users', methods=['POST'])
@require_super_admin
def create_user(_user, _profile):
    """
    Crear un usuario nuevo con asignación de roles (Solo Super Admin)
    ---
    tags:
      - Admin Users
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
            password:
              type: string
            role:
              type: string
              enum: [user, admin, super_admin]
            companyId:
              type: integer
    responses:
      201:
        description: Cuenta pre-creada con envío de correo
      400:
        description: Faltan campos obligatorios o validación cruzada de rol fallida
      409:
        description: El email ya está en uso
      500:
        description: Incidencia al procesar la cola de emails
    """
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    role_name = data.get("role", "user")

    if not email or not password:
        return jsonify({"error": _("Email y contraseña son obligatorios")}), 400

    if Users.query.filter_by(email=email).first():
        return jsonify({"error": _("El email ya está registrado")}), 409

    role_map = {
        "user": UserRole.USER,
        "admin": UserRole.ADMIN,
        "super_admin": UserRole.SUPER_ADMIN,
    }
    role = role_map.get(role_name, UserRole.USER)
    company_id = data.get("companyId")

    if role == UserRole.ADMIN and not company_id:
        return jsonify({"error": _("Los admins deben pertenecer a una empresa")}), 400
    if role == UserRole.SUPER_ADMIN:
        company_id = None

    user, verification_token = _create_pending_user(email, password)
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
    try:
        EmailService.welcome(email, verification_token)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": _("Error al enviar el correo de verificación")}), 500

    return jsonify({
        "mensaje": _("Usuario creado. Debe verificar su correo antes de iniciar sesión."),
        "id": user.id,
    }), 201


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@require_super_admin
def update_user(_user, _profile, user_id):
    """
    Modificar perfil, accesos y credenciales de un usuario (Solo Super Admin)
    ---
    tags:
      - Admin Users
    security:
      - Bearer: []
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
    responses:
      200:
        description: Cambios aplicados con éxito
      403:
        description: Intento de alteración de un Super Admin denegado
      404:
        description: No encontrado
    """
    data = request.get_json() or {}
    user = Users.query.get(user_id)
    if not user or not user.profile:
        return jsonify({"error": _("Usuario no encontrado")}), 404
    if user.profile.role == UserRole.SUPER_ADMIN:
        return jsonify({"error": _("No se puede modificar un superadministrador")}), 403

    new_email = data.get("email")
    if new_email and new_email != user.email:
        if Users.query.filter_by(email=new_email).first():
            return jsonify({"error": _("El email ya está registrado")}), 409
        user.email = new_email

    password = data.get("password")
    if password:
        user.pass_user = generate_password_hash(password)

    profile = user.profile
    if "nombre" in data:
        profile.name = data["nombre"]
    if "apellidos" in data:
        profile.last_name = data["apellidos"]
    if "dni" in data:
        profile.dni = data["dni"]

    role_name = data.get("role")
    if role_name:
        if role_name not in ("user", "admin"):
            return jsonify({"error": _("Rol no válido. Usa user o admin")}), 400
        profile.role = UserRole.ADMIN if role_name == "admin" else UserRole.USER

    if "companyId" in data:
        company_id = data.get("companyId")
        if profile.role == UserRole.ADMIN and not company_id:
            return jsonify({"error": _("Los admins deben pertenecer a una empresa")}), 400
        profile.company_id = company_id

    db.session.commit()
    return jsonify(_user_to_admin_dict(user)), 200


@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@require_super_admin
def update_user_role(_user, _profile, user_id):
    """
    Cambiar de forma directa el rol operativo de un usuario (Solo Super Admin)
    ---
    tags:
      - Admin Users
    security:
      - Bearer: []
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - role
          properties:
            role:
              type: string
              enum: [user, admin]
            companyId:
              type: integer
    responses:
      200:
        description: Permisos actualizados correctamente
      400:
        description: Validación de rol o empresa incorrecta
      403:
        description: Intento de degradación o modificación de un Super Admin prohibido
      404:
        description: Usuario no encontrado
    """
    data = request.get_json() or {}
    role_name = data.get("role")
    if role_name not in ("user", "admin"):
        return jsonify({"error": _("Rol no válido. Usa user o admin")}), 400

    user = Users.query.get(user_id)
    if not user or not user.profile:
        return jsonify({"error": _("Usuario no encontrado")}), 404
    if user.profile.role == UserRole.SUPER_ADMIN:
        return jsonify({"error": _("No se puede modificar un superadministrador")}), 403

    role = UserRole.ADMIN if role_name == "admin" else UserRole.USER
    company_id = data.get("companyId")

    if role == UserRole.ADMIN and not company_id:
        return jsonify({"error": _("Los admins deben pertenecer a una empresa")}), 400

    user.profile.role = role
    user.profile.company_id = company_id if role == UserRole.ADMIN else None
    db.session.commit()

    return jsonify({"mensaje": _("Permisos actualizados correctamente")}), 200