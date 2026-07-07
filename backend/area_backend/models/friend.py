from database import db

class Friend(db.Model):
    __tablename__ = 'friends'
    __table_args__ = {'schema': 'public'}

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('public.users.id', ondelete='CASCADE'), nullable=False)
    friend_id = db.Column(db.BigInteger, db.ForeignKey('public.users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    user = db.relationship('Users', foreign_keys=[user_id], backref=db.backref('friends_list', cascade='all, delete-orphan'))
    friend = db.relationship('Users', foreign_keys=[friend_id])

    __table_args__ = (
        db.UniqueConstraint('user_id', 'friend_id', name='uq_user_friend'),
        {'schema': 'public'}
    )
