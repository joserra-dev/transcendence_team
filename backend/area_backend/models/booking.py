from database import db
from datetime import datetime

class Booking(db.Model):
    __tablename__ = 'booking'
    __table_args__ = {'schema': 'public'}

    id = db.Column(db.BigInteger, primary_key=True)
    id_user = db.Column(db.BigInteger, db.ForeignKey('public.users.id', ondelete='CASCADE'), nullable=False)
    id_space = db.Column(db.BigInteger, db.ForeignKey('public.space.id', ondelete='CASCADE'), nullable=False)
    
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(1), nullable=True)
    rating = db.Column(db.Numeric(2, 0), nullable=True)
    license_plate = db.Column(db.String(15), nullable=False)
    
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
            "license_plate": self.license_plate
        }