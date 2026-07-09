from flask import request
from flask_jwt_extended import decode_token
from flask_socketio import join_room, leave_room

from models.users import UserRole, Users
from utils.chat_helpers import can_access_thread
from utils.realtime import socketio

connected_sessions = {}


@socketio.on('connect')
def handle_connect(auth):
    token = (auth or {}).get('token')
    if not token:
        return False

    try:
        decoded = decode_token(token)
        user_id = int(decoded['sub'])
    except Exception:
        return False

    user = Users.query.get(user_id)
    if not user or not user.profile:
        return False

    profile = user.profile
    if profile.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
        return False

    connected_sessions[request.sid] = {
        'user_id': user_id,
        'profile': profile,
        'active_company_id': None,
    }

    join_room(f'user_{user_id}')

    if profile.role == UserRole.SUPER_ADMIN:
        join_room('superadmin')
    elif profile.company_id:
        join_room(f'company_{profile.company_id}')

    return True


@socketio.on('disconnect')
def handle_disconnect():
    connected_sessions.pop(request.sid, None)


@socketio.on('join_thread')
def handle_join_thread(data):
    session = connected_sessions.get(request.sid)
    if not session:
        return

    company_id = data.get('companyId')
    if not company_id:
        return

    profile = session['profile']
    if not can_access_thread(profile, company_id):
        return

    previous_company_id = session.get('active_company_id')
    if previous_company_id and previous_company_id != company_id:
        leave_room(f'company_{previous_company_id}')

    join_room(f'company_{company_id}')
    session['active_company_id'] = company_id
