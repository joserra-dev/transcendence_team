from datetime import datetime, timezone

from database import db


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    __table_args__ = {'schema': 'public'}

    id = db.Column(db.BigInteger, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('public.company.id'), nullable=False)
    sender_id = db.Column(db.BigInteger, db.ForeignKey('public.users.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    company = db.relationship('Company', backref='chat_messages')
    sender = db.relationship('Users', backref='sent_chat_messages')

    def to_dict(self):
        sender_name = None
        if self.sender and self.sender.profile:
            sender_name = self.sender.profile.name
        return {
            'id': self.id,
            'companyId': self.company_id,
            'senderId': self.sender_id,
            'senderName': sender_name,
            'content': self.content,
            'isRead': self.is_read,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }
