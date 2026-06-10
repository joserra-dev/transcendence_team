from database import db
import enum

class UserRole(enum.Enum):
    USER = 'user'                  # Usuario normal (No pertenece a ninguna empresa)
    ADMIN = 'admin'                # Admin de una empresa (DEBE tener company_id)
    SUPER_ADMIN = 'super_admin'


        
class Users(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'public'}

    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    pass_user = db.Column(db.String(255), nullable=True)
    
    profile = db.relationship('Profiles', backref='user', uselist=False, cascade="all, delete-orphan")
    reservas = db.relationship('Booking', backref='users', cascade="all, delete-orphan", lazy=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            # Evitamos incluir 'pass_user' por seguridad
            # Si tiene perfil, lo serializamos; si no, devolvemos None
            "profile": self.profile.to_dict() if self.profile else None
        }

class Profiles(db.Model):
    __tablename__ = 'profiles'
    __table_args__ = {'schema': 'public'}

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('public.users.id'), unique=True, nullable=False)
    
    # COMPAÑÍA OPCIONAL: nullable=True permite que los usuarios normales y super_admins tengan esto en NULL
    company_id = db.Column(db.Integer, db.ForeignKey('public.company.id'), nullable=True)
    
    dni = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=True)
    birth_day = db.Column(db.Date, nullable=False)
    avatar = db.Column(db.String(500), nullable=True)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)
    iban = db.Column(db.String(34), nullable=True)
    metodo_pago = db.Column(db.String(50), nullable=True, default='iban')
    tarjeta = db.Column(db.String(50), nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "dni": self.dni,
            "name": self.name,
            "last_name": self.last_name,
            "birth_day": self.birth_day.isoformat() if self.birth_day else None, # Las fechas deben ser strings en JSON
            "avatar": self.avatar,
            "role": self.role.value, # .value extrae el string ('user', 'admin') del Enum
            "company_id": self.company_id,
            "iban": self.iban,
            "metodoPago": self.metodo_pago or "iban",
            "tarjeta": self.tarjeta
        }