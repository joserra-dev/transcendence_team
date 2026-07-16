from flask_jwt_extended import decode_token
from flask_socketio import join_room

from chat_events import _get_unread_count, emit_unread_count
from models.users import UserRole, Users
from socketio_ext import socketio


def register_websocket_handlers() -> None:
    @socketio.on('connect')
    def handle_connect(auth):
        if not auth or not auth.get('token'):
            return False

        try:
            decoded = decode_token(auth['token'])
            user_id = int(decoded['sub'])
        except Exception:
            return False

        user = Users.query.get(user_id)
        if not user or not user.profile:
            return False

        profile = user.profile
        if profile.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
            return False

        join_room(f'user:{user_id}')

        if profile.role == UserRole.SUPER_ADMIN:
            join_room('superadmin')
        elif profile.role == UserRole.ADMIN and profile.company_id:
            join_room(f'company:{profile.company_id}')

        emit_unread_count(user_id, _get_unread_count(user, profile))
        return True
