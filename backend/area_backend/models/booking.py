from database import db
from datetime import datetime

class Booking(db.Model):
    __tablename__ = 'booking'
    __table_args__ = {'schema': 'public'}

    id = db.Column(db.BigInteger, primary_key=True)
    id_user = db.Column(db.BigInteger, db.ForeignKey('public.users.id', ondelete='CASCADE'), nullable=False)
    id_space = db.Column(db.BigInteger, db.ForeignKey('public.space.id', ondelete='CASCADE'), nullable=False)
    fecha_inicio_reserva = db.Column(db.Date, nullable=True)
    fecha_fin_reserva = db.Column(db.Date, nullable=True)
    fecha_alta_reserva = db.Column(db.DateTime, default=datetime.utcnow)
    estado_reserva = db.Column(db.String(1), nullable=True)
    puntuacion_reserva = db.Column(db.Numeric(2, 0), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "id_user": self.id_user,
            "id_space": self.id_space,
            "fecha_inicio_reserva": self.fecha_inicio_reserva.isoformat() if self.fecha_inicio_reserva else None,
            "fecha_fin_reserva": self.fecha_fin_reserva.isoformat() if self.fecha_fin_reserva else None,
            "fecha_alta_reserva": self.fecha_alta_reserva.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_alta_reserva else None,
            "estado_reserva": self.estado_reserva,
            "puntuacion_reserva": float(self.puntuacion_reserva) if self.puntuacion_reserva else None
        }