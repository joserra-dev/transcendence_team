from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from database import db
from models.chat_message import ChatMessage
from models.company import Company
from models.users import Profiles, UserRole
from chat_events import emit_messages_read, emit_new_message
from utils.admin_auth import require_admin

chat_bp = Blueprint('chat_bp', __name__, url_prefix='/api/chat')


def _get_company_admin(company_id: int):
    return (
        Profiles.query
        .filter_by(company_id=company_id, role=UserRole.ADMIN)
        .first()
    )


def _can_access_thread(profile: Profiles, company_id: int) -> bool:
    if profile.role == UserRole.SUPER_ADMIN:
        return True
    return profile.role == UserRole.ADMIN and profile.company_id == company_id


def _thread_summary(company: Company, current_user_id: int):
    last_message = (
        ChatMessage.query
        .filter_by(company_id=company.id)
        .order_by(ChatMessage.created_at.desc())
        .first()
    )
    unread_count = (
        ChatMessage.query
        .filter(
            ChatMessage.company_id == company.id,
            ChatMessage.sender_id != current_user_id,
            ChatMessage.is_read.is_(False),
        )
        .count()
    )
    admin_profile = _get_company_admin(company.id)
    admin_name = None
    if admin_profile:
        admin_name = admin_profile.name
        if admin_profile.last_name:
            admin_name = f'{admin_profile.name} {admin_profile.last_name}'.strip()

    return {
        'companyId': company.id,
        'companyName': company.name,
        'adminName': admin_name,
        'lastMessage': last_message.content if last_message else None,
        'lastMessageAt': last_message.created_at.isoformat() if last_message else None,
        'unreadCount': unread_count,
    }


@chat_bp.route('/unread-count', methods=['GET'])
@require_admin
def get_unread_count(user, profile):
    query = ChatMessage.query.filter(
        ChatMessage.sender_id != user.id,
        ChatMessage.is_read.is_(False),
    )
    if profile.role == UserRole.ADMIN:
        if not profile.company_id:
            return jsonify({'count': 0}), 200
        query = query.filter(ChatMessage.company_id == profile.company_id)
    count = query.count()
    return jsonify({'count': count}), 200


@chat_bp.route('/threads', methods=['GET'])
@require_admin
def list_threads(user, profile):
    if profile.role == UserRole.SUPER_ADMIN:
        companies = Company.query.order_by(Company.name.asc()).all()
        threads = [_thread_summary(company, user.id) for company in companies]
    else:
        if not profile.company_id:
            return jsonify({'error': 'El administrador no tiene empresa asignada'}), 400
        company = Company.query.get(profile.company_id)
        if not company:
            return jsonify({'error': 'Empresa no encontrada'}), 404
        threads = [_thread_summary(company, user.id)]

    threads.sort(
        key=lambda t: t['lastMessageAt'] or '',
        reverse=True,
    )
    return jsonify(threads), 200


@chat_bp.route('/threads/<int:company_id>/messages', methods=['GET'])
@require_admin
def get_messages(user, profile, company_id):
    if not _can_access_thread(profile, company_id):
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
    if not _can_access_thread(profile, company_id):
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
    emit_new_message(message)
    return jsonify(message.to_dict()), 201


@chat_bp.route('/threads/<int:company_id>/read', methods=['POST'])
@require_admin
def mark_thread_read(user, profile, company_id):
    if not _can_access_thread(profile, company_id):
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
    emit_messages_read(company_id, user.id)
    return jsonify({'mensaje': 'Mensajes marcados como leídos'}), 200
