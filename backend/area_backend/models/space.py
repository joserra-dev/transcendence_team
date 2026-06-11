from database import db

class Space(db.Model):
    __tablename__ = 'space'
    __table_args__ = {'schema': 'public'}

    id = db.Column(db.BigInteger, primary_key=True)
    id_parking = db.Column(db.BigInteger, db.ForeignKey('public.parking.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(50), nullable=True)
    isvip_plaza = db.Column(db.Boolean, nullable=True)
    tiene_electricidad_plaza = db.Column(db.Boolean, nullable=True)
    estado_plaza = db.Column(db.String(1), nullable=True) # Guarda '0' o '1'
    precio_plaza = db.Column(db.Float, nullable=True)

    # 1. RELACIÓN HACIA PARKING (Necesaria para self.parking.name en to_dict)
    #parking = db.relationship('Parking', backref=db.backref('spaces', lazy=True))
    parking = db.relationship('Parking', back_populates='spaces')

    # 2. RELACIÓN HACIA RESERVAS (Corregida sin backref duplicado, usando cascade limpio)
    # SQLAlchemy ya sabe mapear esto gracias al backref='bookings' que pusimos en Booking.
    # Solo dejamos esta línea si queremos controlar el borrado en cascada (delete-orphan).
    bookings_rel = db.relationship('Booking', cascade="all, delete-orphan", lazy=True)
    

    def to_dict(self):
        return {
            "id": self.id,
            "id_parking": self.id_parking,
            # Mapeos exactos para que hagan match perfecto con tu Angular actual:
            "nombre": self.name,
            "esVip": self.isvip_plaza,
            "tieneElectricidad": self.tiene_electricidad_plaza,
            "estado": self.estado_plaza,
            "precio": self.precio_plaza,
            "parkingNombre": self.parking.name if self.parking else None,
        }