# app.py
import os
from flask import Flask
from flask_mailman import Mail
from database import db, jwt
from flasgger import Swagger
from flask_cors import CORS

from routes.company_routes import company_bp
from routes.users_routes import users_bp
from routes.parking_routes import parking_bp
from routes.space_routes import space_bp
from routes.booking_routes import booking_bp
from routes.access_routes import access_bp
from routes.admin_routes import admin_bp
from routes.public_api_routes import public_api_bp
from routes.status_routes import status_bp


app = Flask(__name__)

CORS(app)
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
app.config['FRONTEND_URL'] = os.environ.get('URL_FRONT', 'http://localhost:8001')

# Inicializamos Mail
mail = Mail(app)
# ==========================================
# 2. INICIALIZACIÓN DE EXTENSIONES DESPUÉS
# ==========================================
# Al llamar a .init_app(app) AQUÍ, db y jwt leerán perfectamente
# las configuraciones que acabamos de setear arriba.
db.init_app(app)
jwt.init_app(app) 


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
app.register_blueprint(access_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(public_api_bp)
app.register_blueprint(status_bp)

# 4. INICIALIZADOR DE BASE DE DATOS
with app.app_context():
    import models
    from seed import seed_database

    db.create_all()
    try:
        db.session.execute(db.text("ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS iban VARCHAR(34);"))
        db.session.execute(db.text("ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS metodo_pago VARCHAR(50);"))
        db.session.execute(db.text("ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS tarjeta VARCHAR(50);"))
        db.session.execute(db.text("ALTER TABLE public.users ADD COLUMN IF NOT EXISTS password_reset_verified BOOLEAN NOT NULL DEFAULT FALSE;"))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f" * Error al alterar la tabla profiles: {e}")
        
    seed_database()

if __name__ == '__main__':
    # Leemos la variable 'FLASK_DEBUG'. Si no existe, por defecto será 'False'
    # .strip().lower() asegura que no afecten los espacios ni las mayúsculas
    debug_env = os.getenv('FLASK_DEBUG', 'False').strip().lower()
    
    # Evaluamos si el string es 'true' o '1' para asignarle el Booleano True
    modo_debug = debug_env in ['true', '1']

    print(f" * Arrancando el servidor con debug={modo_debug}")
    
    app.run(host='0.0.0.0', port=5000, debug=modo_debug)