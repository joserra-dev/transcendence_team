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

    # Relación hacia las reservas
    booking = db.relationship('Booking', backref='Space', cascade="all, delete-orphan", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "id_parking": self.id_parking,
            "name": self.name,
            "isvip_plaza": self.isvip_plaza,
            "tiene_electricidad_plaza": self.tiene_electricidad_plaza,
            "estado_plaza": self.estado_plaza,
            "precio_plaza": self.precio_plaza
        }