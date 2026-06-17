from datetime import timedelta, datetime
import os
from flask import Blueprint, jsonify, request, current_app, redirect
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash 
from flask_jwt_extended import create_access_token, decode_token,jwt_required, get_jwt_identity
from flask_mailman import EmailMessage

from services.email_services import EmailService
from utils.password_validator import PasswordValidator

import secrets

from database import db
from models.users import Users, Profiles

def _user_to_frontend_dict(user):
    profile = user.profile
    is_admin = False
    company_name = None
    
    nombre = ""
    apellidos = ""
    fec_nac = ""
    dni = ""
    iban = ""
    metodo_pago = "iban"
    tarjeta = ""
    
    if profile:
        nombre = profile.name or ""
        apellidos = profile.last_name or ""
        fec_nac = profile.birth_day.isoformat() if profile.birth_day else ""
        dni = profile.dni or ""
        iban = profile.iban or ""
        metodo_pago = profile.metodo_pago or "iban"
        tarjeta = profile.tarjeta or ""
        is_admin = profile.role.value in ['admin', 'super_admin']
        company = profile.company
        if company:
            company_name = company.name
            
    return {
        "id": user.id,
        "nombrePersona": nombre,
        "apellidosPersona": apellidos,
        "fecNacimientoPersona": fec_nac,
        "dniPersona": dni,
        "ibanPersona": iban,
        "metodoPago": metodo_pago,
        "tarjeta": tarjeta,
        "emailPersona": user.email,
        "empresaNombre": company_name,
        "admin": is_admin
    }

# Creamos el Blueprint
users_bp = Blueprint('users_bp', __name__, url_prefix='/api/users')


def _build_frontend_url(path: str) -> str:
    frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:8001').rstrip('/')
    return f"{frontend_url}/{path.lstrip('/')}"


def _build_backend_url(path: str) -> str:
    backend_url = os.getenv('URL_BACK', 'http://localhost:5000').rstrip('/')
    return f"{backend_url}/{path.lstrip('/')}"


def _find_user_by_reset_token(token: str):
    if not token:
        return None
    usuario = Users.query.filter_by(reset_password_token=token).first()
    if not usuario or not usuario.reset_password_expires:
        return None
    if usuario.reset_password_expires < datetime.utcnow():
        return None
    return usuario


def _clear_reset_token(usuario: Users) -> None:
    usuario.reset_password_token = None
    usuario.reset_password_expires = None
    usuario.password_reset_verified = False

@users_bp.route('', methods=['GET'])
def obtener_usuarios():
    """
    Obtiene la lista de usuarios o un usuario específico por ID.
    ---
    tags:
      - Usuarios y Perfiles
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
    user_id = request.args.get('id')

    if user_id:
        usuario = Users.query.get(user_id)
        if usuario:
            return jsonify(usuario.to_dict()), 200
        return jsonify({"error": "Usuario no encontrado"}), 404

    all_users = Users.query.all()
    return jsonify([u.to_dict() for u in all_users]), 200


@users_bp.route('/register', methods=['POST'])
def registrar_usuario():
    """
    Registra un nuevo usuario en el sistema verificando la contraseña.
    ---
    tags:
      - Usuarios y Perfiles
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
            - confirmPassword
          properties:
            email:
              type: string
              example: "carlos@example.com"
            password:
              type: string
              example: "mi_clave_segura123"
            confirmPassword:
              type: string
              example: "mi_clave_segura123"
    responses:
      201:
        description: Usuario creado exitosamente.
      400:
        description: Error de validación (contraseñas no coinciden, email duplicado o faltan datos).
    """
    datos = request.get_json()

    email = datos.get('email')
    password = datos.get('password')
    confirmPassword = datos.get('confirmPassword') # <-- Recorremos el segundo password

    # 1. Validar que vengan absolutamente todos los campos requeridos
    if  not email or not password or not confirmPassword:
        return jsonify({"error": "Todos los campos son obligatorios (email, password, confirmPassword)"}), 400

    # 2. VALIDACIÓN CLAVE: ¿Son iguales las dos contraseñas?
    if password != confirmPassword:
        return jsonify({"error": "Las contraseñas introducidas no coinciden"}), 400

    is_valid, mensagge = PasswordValidator.validar(password, email)
    if not is_valid:
        return jsonify({"error": mensagge}), 400
      
    # 3. Verificar si el email ya existe en PostgreSQL
    usuario_existente = Users.query.filter_by(email=email).first()
    if usuario_existente:
        return jsonify({"error": "Este email ya está registrado"}), 400

    # 4. Si todo está correcto, encriptamos y guardamos
    password_encriptada = generate_password_hash(password)
    verification_token=secrets.token_urlsafe(32)
    nuevo_usuario = Users(
        email = email,
        pass_user = password_encriptada,
        is_verified = False,
        verification_token = verification_token
    )
    try:
        db.session.add(nuevo_usuario)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error al registrar el usuario"}), 500
    try:
        EmailService.welcome(email,verification_token)
        db.session.commit()
<<<<<<< HEAD
        return jsonify({
            "mensaje": "Usuario registrado con éxito",
            "usuario": nuevo_usuario.to_dict()
        }), 201
    except Exception as e:
=======
    except Exception:
>>>>>>> feature/PanelAdmin
        db.session.rollback()
        return jsonify({"error": "Error al enviar el mail de bienvenida"}), 500

    try:
        EmailService.welcome(email, verification_token)
    except Exception as e:
        current_app.logger.error(f"Error enviando correo de bienvenida a {email}: {e}")

    return jsonify({
        "mensaje": "Usuario registrado con éxito. Revisa tu correo para verificar la cuenta.",
        "usuario": nuevo_usuario.to_dict()
    }), 201


@users_bp.route('/verify', methods=['GET'])
def verificar_cuenta():
    token = request.args.get('token')
    if not token:
        return redirect(_build_frontend_url('auth/login-client?verified=0'))

    usuario = Users.query.filter_by(verification_token=token).first()
    if not usuario:
        return redirect(_build_frontend_url('auth/login-client?verified=0'))

    usuario.is_verified = True
    usuario.verification_token = None
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return redirect(_build_frontend_url('auth/login-client?verified=0'))

    return redirect(_build_frontend_url('auth/login-client?verified=1'))


@users_bp.route('/me', methods=['GET'])
@jwt_required() # <--- Esto protege el endpoint, requiere token válido
def get_current_user():
    try:
        # 1. Obtenemos el ID del usuario desde el token JWT
        current_user_id = get_jwt_identity()
        
        # 2. Buscamos al usuario en la base de datos
        user = Users.query.get(current_user_id)
        
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        # 3. Devolvemos los datos necesarios para el perfil
        return jsonify(_user_to_frontend_dict(user)), 200

    except Exception as e:
        return jsonify({"error": "Error al obtener los datos del usuario", "details": str(e)}), 500

@users_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        current_user_id = get_jwt_identity()
        user = Users.query.get(current_user_id)
        if not user:
            return "Usuario no encontrado", 404
            
        data = request.get_json()
        if not data:
            return "Petición inválida", 400
            
        profile = user.profile
        if not profile:
            from datetime import date
            profile = Profiles(
                user_id=user.id,
                name=data.get("nombrePersona", "Usuario"),
                birth_day=date(2000, 1, 1)
            )
            db.session.add(profile)
            
        profile.name = data.get("nombrePersona", profile.name or "")
        profile.last_name = data.get("apellidosPersona", profile.last_name or "")
        profile.metodo_pago = data.get("metodoPago", profile.metodo_pago or "iban")
        profile.iban = data.get("ibanPersona", profile.iban)
        profile.tarjeta = data.get("tarjeta", profile.tarjeta)
        profile.dni = data.get("dniPersona", profile.dni)
        
        fec_nac_str = data.get("fecNacimientoPersona")
        if fec_nac_str:
            from datetime import datetime
            try:
                profile.birth_day = datetime.strptime(fec_nac_str, "%Y-%m-%d").date()
            except ValueError:
                pass
                
        new_password = data.get("passPersona")
        if new_password and new_password.strip() != "":
          is_valid, mensagge = PasswordValidator.validar(new_password)
          if not is_valid:
            return jsonify({"error": mensagge}), 400
          user.pass_user = generate_password_hash(new_password)
            
        db.session.commit()
        return "Perfil actualizado correctamente", 200
        
    except Exception as e:
        db.session.rollback()
        return f"Error interno: {str(e)}", 500

    
@users_bp.route('/login', methods=['POST'])
def autenticar_usuario():
    """
    Registra un nuevo usuario en el sistema verificando la contraseña.
    ---
    tags:
      - Autenticación
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
              example: "carlos@example.com"
            password:
              type: string
              example: "mi_clave_segura123"
    responses:
      200:
        description: Autentificación exitosa.
      400:
        description: Autentificación fallida.
    """
    datos = request.get_json()

    email = datos.get('email')
    password = datos.get('password')
   
    # 1. Validar que vengan absolutamente todos los campos requeridos
    if  not email or not password : 
      return jsonify({"error": "Todos los campos son obligatorios (email, password )"}), 400
    
    # 2. VALIDACIÓN CLAVE: ¿Son iguales las dos contraseñas?
    #if password != confirm_password:
    #    return jsonify({"error": "Las contraseñas introducidas no coinciden"}), 400

    # 3. Verificar si el email ya existe en PostgreSQL
    usuario_existente = Users.query.filter_by(email=email).first()
<<<<<<< HEAD
    
    if not usuario_existente or usuario_existente.is_verified == False:
        return jsonify({"error": "Usuario no existe "}), 401
    
=======
    if not usuario_existente:
        return jsonify({"error": "Credenciales incorrectas"}), 401

>>>>>>> feature/PanelAdmin
    coincide = check_password_hash(usuario_existente.pass_user, password)
    if not coincide:
        return jsonify({"error": "Credenciales incorrectas"}), 401

    # 3.1 Impedir que admins entren por el login de cliente
    perfil = usuario_existente.profile
    if perfil and perfil.role.value in ['admin', 'super_admin']:
        return jsonify({"error": "Debes iniciar sesión desde el acceso de administrador"}), 403

    if not usuario_existente.is_verified:
        return jsonify({"error": "Debes verificar tu correo electrónico antes de iniciar sesión"}), 403
   
    # Modifica la línea 162 para pasarle el ID como string:
    token_acceso = create_access_token(identity=str(usuario_existente.id))

    try:
        return jsonify({
        "mensaje": "¡Login exitoso!",
        "token": token_acceso,
        "user": _user_to_frontend_dict(usuario_existente)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error interno al guardar en la base de datos"}), 500
      
@users_bp.route('/admin-login', methods=['POST'])
def autenticar_admin():
    datos = request.get_json() or {}
    email = datos.get('email')
    password = datos.get('password')

    if not email or not password:
        return jsonify({"error": "Todos los campos son obligatorios (email, password)"}), 400

    usuario = Users.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({"error": "Credenciales incorrectas"}), 401

    if not check_password_hash(usuario.pass_user, password):
        return jsonify({"error": "Credenciales incorrectas"}), 401

    if not usuario.is_verified:
        return jsonify({"error": "Debes verificar tu correo electrónico antes de iniciar sesión"}), 403

    profile = usuario.profile
    if not profile or profile.role.value not in ['admin', 'super_admin']:
        return jsonify({"error": "No tienes permisos de administrador"}), 403

    token_acceso = create_access_token(identity=str(usuario.id))
    return jsonify({
        "mensaje": "¡Login exitoso!",
        "token": token_acceso,
        "user": _user_to_frontend_dict(usuario)
    }), 200


@users_bp.route('/perfil', methods=['GET'])
@jwt_required() # <--- Este decorador obliga a que la petición lleve un token válido
def obtener_perfil():
      """
    Obtiene el perfil del usuario autenticado.
    ---
    tags:
      - Usuarios y Perfiles
      
    security:
      - BearerAuth: []  # <--- ESTO ACTIVA EL CANDADO EN ESTA RUTA
    responses:
      200:
        description: Datos del usuario obtenidos correctamente.
      401:
        description: Token faltante, inválido o expirado.
    """
      usuario_id = get_jwt_identity()
      usuario = Users.query.get(usuario_id)
      
      if not usuario:
          return jsonify({"error": "Usuario no encontrado"}), 404
          
      return jsonify({
          "usuario": _user_to_frontend_dict(usuario)
      }), 200

      
@users_bp.route('/forgot-password', methods=['POST'])
def solicitar_recuperacion():
    """
    Solicita la recuperación de contraseña enviando un correo con un enlace seguro.
    ---
    tags:
      - Autenticación y Usuarios
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
          properties:
            email:
              type: string
              format: email
              example: usuario@correo.com
              description: El correo electrónico de la cuenta que se quiere recuperar.
    responses:
      200:
        description: Solicitud procesada. Por seguridad, se devuelve el mismo mensaje exista o no el correo.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Si el correo existe, se enviarán las instrucciones."
      400:
        description: El formato del JSON o los datos enviados no son válidos.
      500:
        description: Error interno del servidor al procesar la solicitud o enviar el correo.
    """
    data = request.get_json() or {}
    email = data.get('email')

    if not email:
        return jsonify({"error": "El campo email es obligatorio"}), 400

    normalized_email = email.strip().lower()
    usuario = Users.query.filter(func.lower(Users.email) == normalized_email).first()

    if usuario:
        reset_token = secrets.token_urlsafe(32)
        usuario.reset_password_token = reset_token
        usuario.reset_password_expires = datetime.utcnow() + timedelta(hours=1)
        usuario.password_reset_verified = False
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error guardando token de recuperación: {e}")
            return jsonify({"error": "Error interno al procesar la solicitud"}), 500

        url_recuperacion = _build_backend_url(f"api/users/reset-password/verify?token={reset_token}")

        try:
            EmailService.forgot(
                destinatario=usuario.email,
                user_name=usuario.email,
                recovery_url=url_recuperacion
            )
            current_app.logger.info(f"Correo de recuperación enviado a {usuario.email}")
        except Exception as e:
            current_app.logger.error(f"Error enviando correo de recuperación: {e}")
            return jsonify({"error": "Error interno al procesar la solicitud", "details": str(e)}), 500

    return jsonify({"message": "Si el correo existe, se enviarán las instrucciones."}), 200


@users_bp.route('/reset-password/verify', methods=['GET'])
def verificar_reset_password():
    token = request.args.get('token')
    if not token:
        return redirect(_build_frontend_url('auth/reset-password?reset=0'))

    usuario = Users.query.filter_by(reset_password_token=token).first()
    if not usuario or not usuario.reset_password_expires or usuario.reset_password_expires < datetime.utcnow():
        return redirect(_build_frontend_url('auth/reset-password?reset=0'))

    form_token = secrets.token_urlsafe(32)
    usuario.password_reset_verified = True
    usuario.reset_password_token = form_token
    usuario.reset_password_expires = datetime.utcnow() + timedelta(hours=1)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return redirect(_build_frontend_url('auth/reset-password?reset=0'))

    return redirect(_build_frontend_url(f'auth/reset-password?token={form_token}'))


@users_bp.route('/reset-password', methods=['POST'])
def restablecer_password():
    data = request.get_json() or {}
    token = data.get('token')
    new_password = data.get('password')
    confirm_password = data.get('confirmPassword')

    if not token or not new_password or not confirm_password:
        return jsonify({"error": "token, password y confirmPassword son obligatorios"}), 400

    if new_password != confirm_password:
        return jsonify({"error": "Las contraseñas introducidas no coinciden"}), 400

    usuario = _find_user_by_reset_token(token)
    if not usuario or not usuario.password_reset_verified:
        return jsonify({"error": "El enlace de recuperación no es válido o ha caducado"}), 400

    usuario.pass_user = generate_password_hash(new_password)
    _clear_reset_token(usuario)

    try:
        db.session.commit()
        return jsonify({"message": "Contraseña actualizada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": "Error interno al procesar la solicitud", "details": str(e)}), 500
      
@users_bp.route('/verify', methods=['GET'])
def verify_account():
    """
    Endpoint para verificar la cuenta de usuario mediante el token enviado por correo.
    Se accede mediante un GET (ej: /api/users/verify?token=XYZ...)
    """
    token = request.args.get('token')
    
    if not token:
        return jsonify({
            "status": "error",
            "message": "Falta el token de verificación."
        }), 400

    user = Users.query.filter_by(verification_token=token).first()

    if not user:
        return jsonify({
            "status": "error",
            "message": "El token no es válido o ya ha sido utilizado."
        }), 400

    try:
        user.is_verified = True
        user.verification_token = None
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "¡Cuenta verificada con éxito! Ya puedes iniciar sesión."
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": f"Hubo un problema al verificar la cuenta: {str(e)}"
        }), 500