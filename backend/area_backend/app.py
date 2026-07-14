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


app = Flask(__name__)

# Configurar CORS con orígenes específicos en lugar de permitir todos.
# Soporta varios orígenes separados por comas (p. ej. dev y prod).
frontend_origins = os.getenv('URL_FRONT', 'http://localhost:4200').split(',')
CORS(app, resources={r"/api/*": {"origins": frontend_origins}})
# ==========================================
# 1. PASO CRUCIAL: CONFIGURACIÓN PRIMERO
# ==========================================
# Definimos las claves directamente en la app básica
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'mi_super_clave_secreta_123')
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

# Configuración de Flask-Babel
app.config['BABEL_DEFAULT_LOCALE'] = 'es'
app.config['BABEL_SUPPORTED_LOCALES'] = ['es', 'eu', 'en']

# Inicializamos Mail
mail = Mail(app)

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

# 4. INICIALIZADOR DE BASE DE DATOS
# En desarrollo se fuerza el seed. En producción solo si la base de datos está vacía.
with app.app_context():
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
    