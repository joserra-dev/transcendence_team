from models.chat_message import ChatMessage
from models.users import Profiles, UserRole, Users
from socketio_ext import socketio


def _get_unread_count(user: Users, profile: Profiles) -> int:
    query = ChatMessage.query.filter(
        ChatMessage.sender_id != user.id,
        ChatMessage.is_read.is_(False),
    )
    if profile.role == UserRole.ADMIN:
        if not profile.company_id:
            return 0
        query = query.filter(ChatMessage.company_id == profile.company_id)
    return query.count()


def _get_company_admin_user_id(company_id: int) -> int | None:
    profile = (
        Profiles.query
        .filter_by(company_id=company_id, role=UserRole.ADMIN)
        .first()
    )
    return profile.user_id if profile else None


def _get_super_admin_user_ids() -> list[int]:
    profiles = Profiles.query.filter_by(role=UserRole.SUPER_ADMIN).all()
    return [p.user_id for p in profiles]


def emit_unread_count(user_id: int, count: int) -> None:
    socketio.emit('unread_count', {'count': count}, room=f'user:{user_id}')


def notify_unread_recipients(sender_id: int, company_id: int) -> None:
    sender = Users.query.get(sender_id)
    if not sender or not sender.profile:
        return

    sender_profile = sender.profile

    if sender_profile.role == UserRole.ADMIN:
        for user_id in _get_super_admin_user_ids():
            if user_id == sender_id:
                continue
            user = Users.query.get(user_id)
            if user and user.profile:
                emit_unread_count(user_id, _get_unread_count(user, user.profile))
    elif sender_profile.role == UserRole.SUPER_ADMIN:
        admin_user_id = _get_company_admin_user_id(company_id)
        if admin_user_id and admin_user_id != sender_id:
            admin_user = Users.query.get(admin_user_id)
            if admin_user and admin_user.profile:
                emit_unread_count(
                    admin_user_id,
                    _get_unread_count(admin_user, admin_user.profile),
                )


def emit_new_message(message: ChatMessage) -> None:
    msg_dict = message.to_dict()
    company_id = message.company_id

    socketio.emit('new_message', msg_dict, room=f'company:{company_id}')
    socketio.emit('new_message', msg_dict, room='superadmin')
    notify_unread_recipients(message.sender_id, company_id)


def emit_messages_read(company_id: int, reader_id: int) -> None:
    payload = {'companyId': company_id, 'readerId': reader_id}
    socketio.emit('messages_read', payload, room=f'company:{company_id}')
    socketio.emit('messages_read', payload, room='superadmin')

    reader = Users.query.get(reader_id)
    if reader and reader.profile:
        emit_unread_count(reader_id, _get_unread_count(reader, reader.profile))

    sender_ids: set[int] = set()
    messages = (
        ChatMessage.query
        .filter_by(company_id=company_id)
        .filter(ChatMessage.sender_id != reader_id)
        .all()
    )
    for msg in messages:
        sender_ids.add(msg.sender_id)

    for sender_id in sender_ids:
        sender = Users.query.get(sender_id)
        if sender and sender.profile:
            emit_unread_count(sender_id, _get_unread_count(sender, sender.profile))
