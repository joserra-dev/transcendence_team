import os
from flask import Flask, request
from flask_mailman import Mail
from database import db, jwt
from flasgger import Swagger
from flask_cors import CORS
from flask_babel import Babel

from routes.company_routes import company_bp
from routes.users_routes import users_bp
from routes.parking_routes import parking_bp
from routes.space_routes import space_bp
from routes.booking_routes import booking_bp
from routes.admin_routes import admin_bp
from routes.access_routes import access_bp
from routes.public_api_routes import public_api_bp
from routes.status_routes import status_bp
from routes.friend_routes import friends_bp
from routes.chat_routes import chat_bp
from socketio_ext import socketio
from websocket_handlers import register_websocket_handlers


app = Flask(__name__)

# Configurar CORS.
# - Desarrollo (FLASK_ENV=development): se permite cualquier origen, ya que es
#   normal acceder desde localhost/127.0.0.1/el hostname de la máquina y simplifica
#   el trabajo local sin tener que alinear URL_FRONT con el Origin del navegador.
# - Producción: orígenes restringidos a URL_FRONT (separados por comas), para no
#   exponer la API a cualquier sitio (CWE-942).
is_development = os.getenv('FLASK_ENV') == 'development'
if is_development:
    frontend_origins = "*"
else:
    frontend_origins = [
        origin.strip().rstrip('/').lower()
        for origin in os.getenv('URL_FRONT', 'http://localhost:4200').split(',')
        if origin.strip()
    ]
CORS(app, resources={r"/api/*": {"origins": frontend_origins}})
socketio.init_app(
    app,
    cors_allowed_origins=frontend_origins,
    async_mode='eventlet',
    logger=False,
    engineio_logger=False,
)
# ==========================================
# 1. PASO CRUCIAL: CONFIGURACIÓN PRIMERO
# ==========================================
# Definimos las claves directamente en la app básica
jwt_secret_key = os.getenv('JWT_SECRET_KEY')
if not jwt_secret_key:
    raise RuntimeError(
        "JWT_SECRET_KEY no está definida. Define JWT_SECRET_KEY en el archivo .env "
        "(p. ej. con 'python -c \"import secrets; print(secrets.token_hex(32))\"'). "
        "El arranque se aborta por seguridad."
    )
app.config['JWT_SECRET_KEY'] = jwt_secret_key

# Expiración del token de acceso (CWE-613): los tokens dejan de ser válidos
# tras este tiempo, limitando el impacto de un token filtrado. Se configura en
# minutos vía JWT_ACCESS_TOKEN_EXPIRES (por defecto 120 = 2 horas).
from datetime import timedelta
_jwt_expires_minutes = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '120'))
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=_jwt_expires_minutes)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://defaultdb_uk1q_user:password@db:5432/defaultdb')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get(
    'MAIL_DEFAULT_SENDER',
    os.environ.get('MAIL_USERNAME', 'noreply@local.test')
)
app.config['FRONTEND_URL'] = os.environ.get('URL_FRONT', 'https://localhost:8001')

# Rate limiting (CWE-307): protege login/registro/recuperación contra fuerza bruta.
# En producción usa Redis compartido; si no está disponible, cae a memoria (por-worker).
_ratelimit_uri = os.getenv('RATELIMIT_STORAGE_URI', 'memory://')
if _ratelimit_uri.startswith('redis'):
    try:
        import redis as _redis
        _client = _redis.from_url(_ratelimit_uri)
        _client.ping()
    except Exception as _e:
        print(f"ADVERTENCIA: Redis no disponible ({_e}). Usando rate limiting en memoria (no compartido).")
        _ratelimit_uri = 'memory://'
app.config['RATELIMIT_STORAGE_URI'] = _ratelimit_uri
app.config['RATELIMIT_DEFAULT'] = "200 per hour"
app.config['RATELIMIT_HEADERS'] = True

# Configuración de Flask-Babel
app.config['BABEL_DEFAULT_LOCALE'] = 'es'
app.config['BABEL_SUPPORTED_LOCALES'] = ['es', 'eu', 'en']

# Inicializamos Mail
mail = Mail(app)

# Inicializamos Limiter (rate limiting / fuerza bruta)
from database import limiter
limiter.init_app(app)

# ==========================================
# 2. INICIALIZACIÓN DE EXTENSIONES DESPUÉS
# ==========================================
db.init_app(app)
jwt.init_app(app) 

# Función que Babel ejecutará en cada petición para elegir el idioma
def get_locale():
    idiomas_soportados = app.config.get('BABEL_SUPPORTED_LOCALES', ['es', 'eu', 'en'])
    
    # Priority 1: Buscar si el parámetro explícito viene en la URL (?lang=es)
    lang_url = request.args.get('lang')
    if lang_url and lang_url.lower() in idiomas_soportados:
        return lang_url

    # Priority 2: Ver si algún Blueprint interceptó y guardó ya un idioma válido
    if hasattr(request, 'babel_locale') and request.babel_locale in idiomas_soportados:
        return request.babel_locale
        
    # Priority 3: Analizar la cabecera 'Accept-Language' del navegador/cliente
    match_cabecera = request.accept_languages.best_match(idiomas_soportados)
    if match_cabecera:
        return match_cabecera
        
    # Priority 4: Idioma base del sistema por defecto
    return app.config.get('BABEL_DEFAULT_LOCALE', 'es')

# Inicialización de Flask-Babel pasándole la función selectora corregida
babel = Babel(app, locale_selector=get_locale)


swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "API de ft_transcendence",
        "description": "Documentación de la API con autenticación JWT",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Introduce tu token JWT en este formato: Bearer <TU_TOKEN>"
        }
    }
}
swagger = Swagger(app,  template=swagger_template)

# 3. REGISTRO DE BLUEPRINTS
app.register_blueprint(company_bp)
app.register_blueprint(users_bp)
app.register_blueprint(parking_bp)
app.register_blueprint(space_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(access_bp)
app.register_blueprint(public_api_bp)
app.register_blueprint(status_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(friends_bp)
register_websocket_handlers()

# 4. INICIALIZADOR DE BASE DE DATOS
# En desarrollo se fuerza el seed. En producción solo si la base de datos está vacía.
with app.app_context():
    from sqlalchemy import text

    def _ensure_schema() -> None:
        try:
            db.session.execute(text(
                "ALTER TABLE public.users "
                "ADD COLUMN IF NOT EXISTS is_active boolean NOT NULL DEFAULT true"
            ))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            app.logger.warning(f" * No se pudo aplicar migración is_active: {e}")

    _ensure_schema()

    def _should_seed_database() -> bool:
        if os.getenv('FLASK_ENV') == 'development':
            return True

        from models.users import Users
        return Users.query.first() is None

    if _should_seed_database():
        from seed import seed_database
        try:
            seed_database()
        except Exception as e:
            app.logger.error(f" * Error en seed_database: {e}")

if __name__ == '__main__':
    debug_env = os.getenv('FLASK_DEBUG', 'False').strip().lower()
    modo_debug = debug_env in ['true', '1']

    print(f" * Arrancando el servidor con debug={modo_debug}")
    app.run(host='0.0.0.0', port=5000, debug=modo_debug)
    