import os
import sys
import logging
from datetime import timedelta

# Configuración básica del logger nativo de Python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

REQUIRED_ENV_VARS = [
    'FLASK_ENV',
    'FLASK_DEBUG',
    'BACK_SCHEME',
    'FRONT_PORT',
    'URL_FRONT',
    'BACK_PORT',
    'URL_BACK',
    'POSTGRES_DB',
    'POSTGRES_USER',
    'POSTGRES_PASSWORD',
    'POSTGRES_PORT',
    'DATABASE_URL',
    'JWT_SECRET_KEY',
    'JWT_ACCESS_TOKEN_EXPIRES',
    'PUBLIC_API_KEY',
    'PUBLIC_API_RATE_LIMIT',
    'RATELIMIT_STORAGE_URI',
    'STRIPE_KEY',
    'MAIL_SERVER',
    'MAIL_PORT',
    'MAIL_USE_TLS',
    'MAIL_USERNAME',
    'MAIL_PASSWORD',
    'SUPER_ADMIN_PASSWORD',
    'MAIL_DEFAULT_SENDER'
]

def check_env_vars():
    missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    
    if missing_vars:
        logger.error("[ERROR FATAL] Faltan las siguientes variables de entorno requeridas:")
        for var in missing_vars:
            logger.error(f"   - {var}")
        logger.error("El servidor no se iniciará por motivos de seguridad e integridad.")
        sys.exit(1)

# Validar antes de ejecutar cualquier lógica o importar Flask
check_env_vars()
logger.info("✅ Variables de entorno requeridas validadas con éxito.")

# ==========================================
# IMPORTS Y CONFIGURACIÓN DE FLASK
# ==========================================
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

# Reutilizar la configuración del logger nativo dentro de Flask
app.logger.handlers = logger.handlers
app.logger.setLevel(logger.level)

# Configurar CORS
is_development = os.getenv('FLASK_ENV') == 'development'
if is_development:
    frontend_origins = "*"
else:
    frontend_origins = [
        origin.strip().rstrip('/').lower()
        for origin in os.getenv('URL_FRONT').split(',')
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
# 1. CONFIGURACIÓN DE LA APLICACIÓN
# ==========================================
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

_jwt_expires_minutes = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '120'))
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=_jwt_expires_minutes)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración de Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv(
    'MAIL_DEFAULT_SENDER',
    os.getenv('MAIL_USERNAME', 'noreply@local.test')
)
app.config['FRONTEND_URL'] = os.getenv('URL_FRONT')

# Rate limiting
_ratelimit_uri = os.getenv('RATELIMIT_STORAGE_URI', 'memory://')
if _ratelimit_uri.startswith('redis'):
    try:
        import redis as _redis
        _client = _redis.from_url(_ratelimit_uri)
        _client.ping()
    except Exception as _e:
        app.logger.warning(f"ADVERTENCIA: Redis no disponible ({_e}). Usando rate limiting en memoria (no compartido).")
        _ratelimit_uri = 'memory://'

app.config['RATELIMIT_STORAGE_URI'] = _ratelimit_uri
app.config['RATELIMIT_DEFAULT'] = "200 per hour"
app.config['RATELIMIT_HEADERS'] = True

# Configuración de Flask-Babel
app.config['BABEL_DEFAULT_LOCALE'] = 'es'
app.config['BABEL_SUPPORTED_LOCALES'] = ['es', 'eu', 'en']

# Inicializar extensiones
mail = Mail(app)

from database import limiter
limiter.init_app(app)

db.init_app(app)
jwt.init_app(app)

# Selector de idioma para Babel
def get_locale():
    idiomas_soportados = app.config.get('BABEL_SUPPORTED_LOCALES', ['es', 'eu', 'en'])
    
    lang_url = request.args.get('lang')
    if lang_url and lang_url.lower() in idiomas_soportados:
        return lang_url

    if hasattr(request, 'babel_locale') and request.babel_locale in idiomas_soportados:
        return request.babel_locale
        
    match_cabecera = request.accept_languages.best_match(idiomas_soportados)
    if match_cabecera:
        return match_cabecera
        
    return app.config.get('BABEL_DEFAULT_LOCALE', 'es')

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
swagger = Swagger(app, template=swagger_template)

# ==========================================
# 2. REGISTRO DE BLUEPRINTS
# ==========================================
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

# ==========================================
# 3. INICIALIZADOR DE BASE DE DATOS Y SEED
# ==========================================
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

# ==========================================
# 4. ARRANQUE DEL SERVIDOR
# ==========================================
if __name__ == '__main__':
    debug_env = os.getenv('FLASK_DEBUG', 'False').strip().lower()
    modo_debug = debug_env in ['true', '1']
    
    port = int(os.getenv('BACK_PORT', 5000))

    logger.info(f" * Arrancando el servidor en el puerto {port} con debug={modo_debug}")
    socketio.run(app, host='0.0.0.0', port=port, debug=modo_debug)