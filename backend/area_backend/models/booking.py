from database import db
from datetime import datetime


class BookingStatus:
    """Constantes para los estados de reserva."""
    PENDING = '0'      # Pendiente de pago
    CONFIRMED = '1'    # Pagada/Confirmada
    PROCESSING = '2'   # En proceso de pago (Stripe)


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

    # NUEVOS CAMPOS FISCALES (Nacen vacíos. Se rellenan ÚNICAMENTE al pagar)
    invoice_serie = db.Column(db.String(20), nullable=True)
    invoice_number = db.Column(db.String(20), nullable=True)
    invoice_date = db.Column(db.Date, nullable=True)
    tbai_id = db.Column(db.String(100), nullable=True)       # ID Legal TicketBAI
    tbai_qr_code = db.Column(db.Text, nullable=True)         # Imagen del QR en formato Base64

    user = db.relationship('Users', back_populates='bookings')
    space = db.relationship('Space', back_populates='bookings_rel')

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
            "total_price": self.total_price,
            
            "invoice_full": f"{self.invoice_serie}-{self.invoice_number}" if self.invoice_number else None,
            "invoice_date": self.invoice_date.isoformat() if self.invoice_date else None,
            "tbai_id": self.tbai_id,
            "qr_image_base64": self.tbai_qr_code
        }