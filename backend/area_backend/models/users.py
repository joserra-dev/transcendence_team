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
    
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_token = db.Column(db.String(255), unique=True, nullable=True)
    verification_expires = db.Column(db.DateTime, nullable=True)

    reset_password_token = db.Column(db.String(255), unique=True, nullable=True)
    reset_password_expires = db.Column(db.DateTime, nullable=True)
    password_reset_verified = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    profile = db.relationship('Profiles', back_populates='user', uselist=False, cascade="all, delete-orphan")
    bookings = db.relationship('Booking', back_populates='user', lazy=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "isActive": self.is_active,
            "profile": self.profile.to_dict() if self.profile else None
        }

class Profiles(db.Model):
    __tablename__ = 'profiles'
    __table_args__ = {'schema': 'public'}

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('public.users.id', ondelete='CASCADE'), unique=True, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('public.company.id'), nullable=True)
    
    dni = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=True)
    birth_day = db.Column(db.Date, nullable=False)
    avatar = db.Column(db.String(500), nullable=True)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)
    #iban = db.Column(db.String(34), nullable=True)
    #metodo_pago = db.Column(db.String(50), nullable=True, default='iban')
    #tarjeta = db.Column(db.String(50), nullable=True)
    
    user = db.relationship('Users', back_populates='profile')
    company = db.relationship('Company', back_populates='users')
    
    def to_dict(self):
        return {
            "id": self.id,
            "dni": self.dni,
            "name": self.name,
            "last_name": self.last_name,
            "birth_day": self.birth_day.isoformat() if self.birth_day else None,
            "avatar": self.avatar,
            "role": self.role.value,
            "company_id": self.company_id
            #"iban": self.iban,
            #"metodoPago": self.metodo_pago or "iban",
            #"tarjeta": self.tarjeta
        }