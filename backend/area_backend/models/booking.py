from database import db
from datetime import datetime


class BookingStatus:
    """Constantes para los estados de reserva."""
    PENDING = '0'       # Pendiente de pago (cancelada por el usuario desde Stripe)
    CONFIRMED = '1'     # Pagada/Confirmada
    PROCESSING = '2'    # En proceso de pago (Stripe)
    CANCELLED = '3'     # Cancelada por el sistema (expirada por falta de pago)


class Booking(db.Model):
    __tablename__ = 'booking'
    __table_args__ = {'schema': 'public'}

    id = db.Column(db.BigInteger, primary_key=True)
    id_user = db.Column(db.BigInteger, db.ForeignKey('public.users.id', ondelete='SET NULL'), nullable=True)
    id_space = db.Column(db.BigInteger, db.ForeignKey('public.space.id', ondelete='CASCADE'), nullable=False)
    
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(1), nullable=True) # Ej: '0'=Pendiente, '1'=Pagado/Confirmado
    rating = db.Column(db.Numeric(2, 0), nullable=True)
    license_plate = db.Column(db.String(15), nullable=False)
    customer_email = db.Column(db.String(255), nullable=True)
    customer_name = db.Column(db.String(255), nullable=True)
    
    # NUEVO CAMPO MONETARIO: El coste total calculado de la estancia
    total_price = db.Column(db.Float, nullable=False, default=0.0)
    user = db.relationship('Users', back_populates='bookings')
    space = db.relationship('Space', back_populates='bookings_rel')
    stripe_session_id = db.Column(db.String(255), nullable=True)
    confirm_token = db.Column(db.String(64), nullable=True, unique=True)

    def to_dict(self):
        return {
            "id": self.id,
            "id_user": self.id_user,
            "id_space": self.id_space,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            "status": self.status,
            "rating": float(self.rating) if self.rating is not None else None,
            "license_plate": self.license_plate,
            "total_price": self.total_price
        }