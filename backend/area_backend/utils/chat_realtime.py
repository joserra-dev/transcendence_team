from models.company import Company
from models.users import Profiles, UserRole, Users

from utils.chat_helpers import thread_summary, unread_count_for_profile
from utils.realtime import socketio


def _user_room(user_id: int) -> str:
    return f'user_{user_id}'


def _company_room(company_id: int) -> str:
    return f'company_{company_id}'


def _emit_unread_count(user_id: int, profile: Profiles):
    count = unread_count_for_profile(user_id, profile)
    socketio.emit('unread_count', {'count': count}, room=_user_room(user_id))


def _notify_recipients_unread(sender_id: int, company_id: int):
    sender = Users.query.get(sender_id)
    if not sender or not sender.profile:
        return

    sender_role = sender.profile.role

    if sender_role == UserRole.ADMIN:
        super_admins = Profiles.query.filter_by(role=UserRole.SUPER_ADMIN).all()
        for profile in super_admins:
            _emit_unread_count(profile.user_id, profile)
    elif sender_role == UserRole.SUPER_ADMIN:
        admin_profile = (
            Profiles.query
            .filter_by(company_id=company_id, role=UserRole.ADMIN)
            .first()
        )
        if admin_profile:
            _emit_unread_count(admin_profile.user_id, admin_profile)


def notify_new_message(message):
    data = message.to_dict()
    company_id = message.company_id

    socketio.emit('new_message', data, room=_company_room(company_id))

    company = Company.query.get(company_id)
    if company:
        super_admins = Profiles.query.filter_by(role=UserRole.SUPER_ADMIN).all()
        for profile in super_admins:
            summary = thread_summary(company, profile.user_id)
            socketio.emit('thread_updated', summary, room=_user_room(profile.user_id))

        admin_profile = (
            Profiles.query
            .filter_by(company_id=company_id, role=UserRole.ADMIN)
            .first()
        )
        if admin_profile:
            summary = thread_summary(company, admin_profile.user_id)
            socketio.emit('thread_updated', summary, room=_user_room(admin_profile.user_id))

    _notify_recipients_unread(message.sender_id, company_id)


def notify_messages_read(company_id: int, reader_id: int):
    socketio.emit(
        'messages_read',
        {'companyId': company_id, 'readerId': reader_id},
        room=_company_room(company_id),
    )

    reader = Users.query.get(reader_id)
    if reader and reader.profile:
        _emit_unread_count(reader_id, reader.profile)

    company = Company.query.get(company_id)
    if not company:
        return

    super_admins = Profiles.query.filter_by(role=UserRole.SUPER_ADMIN).all()
    for profile in super_admins:
        summary = thread_summary(company, profile.user_id)
        socketio.emit('thread_updated', summary, room=_user_room(profile.user_id))

    admin_profile = (
        Profiles.query
        .filter_by(company_id=company_id, role=UserRole.ADMIN)
        .first()
    )
    if admin_profile:
        summary = thread_summary(company, admin_profile.user_id)
        socketio.emit('thread_updated', summary, room=_user_room(admin_profile.user_id))
