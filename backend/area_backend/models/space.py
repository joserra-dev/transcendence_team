from database import db

class Space(db.Model):
    __tablename__ = 'space'
    __table_args__ = {'schema': 'public'}

    id = db.Column(db.BigInteger, primary_key=True)
    id_parking = db.Column(db.BigInteger, db.ForeignKey('public.parking.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(50), nullable=True)
    isvip = db.Column(db.Boolean, nullable=True)
    has_electr= db.Column(db.Boolean, nullable=True)
    status = db.Column(db.String(1), nullable=True)
    price = db.Column(db.Float, nullable=True)

    parking = db.relationship('Parking', back_populates='spaces')
    bookings_rel = db.relationship('Booking', back_populates='space', cascade="all, delete-orphan", lazy=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "id_parking": self.id_parking,
            "name": self.name,
            "isVip": self.isvip,
            "hasElectr": self.has_electr,
            "status": self.status,
            "price": self.price,
            "parkingName": self.parking.name if self.parking else None,
        }