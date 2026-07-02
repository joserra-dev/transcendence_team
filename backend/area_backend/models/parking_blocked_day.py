from database import db
from datetime import datetime


class ParkingBlockedDay(db.Model):
    __tablename__ = 'parking_blocked_day'
    __table_args__ = (
        db.UniqueConstraint('id_parking', 'day', name='uq_parking_blocked_day'),
        {'schema': 'public'},
    )

    id = db.Column(db.BigInteger, primary_key=True)
    id_parking = db.Column(
        db.BigInteger,
        db.ForeignKey('public.parking.id', ondelete='CASCADE'),
        nullable=False,
    )
    day = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "parkingId": self.id_parking,
            "day": self.day.isoformat() if self.day else None,
        }
