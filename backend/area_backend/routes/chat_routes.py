from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from database import db
from models.chat_message import ChatMessage
from models.company import Company
from models.users import UserRole
from utils.admin_auth import require_admin
from utils.chat_helpers import can_access_thread, thread_summary
from utils.chat_realtime import notify_messages_read, notify_new_message

chat_bp = Blueprint('chat_bp', __name__, url_prefix='/api/chat')


@chat_bp.route('/unread-count', methods=['GET'])
@require_admin
def get_unread_count(user, profile):
    from utils.chat_helpers import unread_count_for_profile

    count = unread_count_for_profile(user.id, profile)
    return jsonify({'count': count}), 200


@chat_bp.route('/threads', methods=['GET'])
@require_admin
def list_threads(user, profile):
    if profile.role == UserRole.SUPER_ADMIN:
        companies = Company.query.order_by(Company.name.asc()).all()
        threads = [thread_summary(company, user.id) for company in companies]
    else:
        if not profile.company_id:
            return jsonify({'error': 'El administrador no tiene empresa asignada'}), 400
        company = Company.query.get(profile.company_id)
        if not company:
            return jsonify({'error': 'Empresa no encontrada'}), 404
        threads = [thread_summary(company, user.id)]

    threads.sort(
        key=lambda t: t['lastMessageAt'] or '',
        reverse=True,
    )
    return jsonify(threads), 200


@chat_bp.route('/threads/<int:company_id>/messages', methods=['GET'])
@require_admin
def get_messages(user, profile, company_id):
    if not can_access_thread(profile, company_id):
        return jsonify({'error': 'No autorizado'}), 403

    company = Company.query.get(company_id)
    if not company:
        return jsonify({'error': 'Empresa no encontrada'}), 404

    messages = (
        ChatMessage.query
        .filter_by(company_id=company_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return jsonify([msg.to_dict() for msg in messages]), 200


@chat_bp.route('/threads/<int:company_id>/messages', methods=['POST'])
@require_admin
def send_message(user, profile, company_id):
    if not can_access_thread(profile, company_id):
        return jsonify({'error': 'No autorizado'}), 403

    company = Company.query.get(company_id)
    if not company:
        return jsonify({'error': 'Empresa no encontrada'}), 404

    data = request.get_json(silent=True) or {}
    content = (data.get('content') or '').strip()
    if not content:
        return jsonify({'error': 'El mensaje no puede estar vacío'}), 400
    if len(content) > 2000:
        return jsonify({'error': 'El mensaje es demasiado largo'}), 400

    message = ChatMessage(
        company_id=company_id,
        sender_id=user.id,
        content=content,
        is_read=False,
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(message)
    db.session.commit()

    message_dict = message.to_dict()
    notify_new_message(message)

    return jsonify(message_dict), 201


@chat_bp.route('/threads/<int:company_id>/read', methods=['POST'])
@require_admin
def mark_thread_read(user, profile, company_id):
    if not can_access_thread(profile, company_id):
        return jsonify({'error': 'No autorizado'}), 403

    (
        ChatMessage.query
        .filter(
            ChatMessage.company_id == company_id,
            ChatMessage.sender_id != user.id,
            ChatMessage.is_read.is_(False),
        )
        .update({'is_read': True}, synchronize_session=False)
    )
    db.session.commit()

    notify_messages_read(company_id, user.id)

    return jsonify({'mensaje': 'Mensajes marcados como leídos'}), 200
