from datetime import date, datetime

from database import db


class SpaceBlockedDay(db.Model):
    __tablename__ = 'space_blocked_day'
    __table_args__ = (
        db.UniqueConstraint('id_space', 'day', name='uq_space_blocked_day'),
        {'schema': 'public'},
    )

    id = db.Column(db.BigInteger, primary_key=True)
    id_space = db.Column(
        db.BigInteger,
        db.ForeignKey('public.space.id', ondelete='CASCADE'),
        nullable=False,
    )
    day = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def is_blocked_in_range(space_id: int, start_date: date, end_date: date) -> bool:
        if not space_id or not start_date or not end_date:
            return False

        return (
            SpaceBlockedDay.query.filter(
                SpaceBlockedDay.id_space == space_id,
                SpaceBlockedDay.day >= start_date,
                SpaceBlockedDay.day < end_date,
            ).first()
            is not None
        )

    def to_dict(self):
        return {
            "id": self.id,
            "spaceId": self.id_space,
            "day": self.day.isoformat() if self.day else None,
        }
