from models.chat_message import ChatMessage
from models.company import Company
from models.users import Profiles, UserRole


def get_company_admin(company_id: int):
    return (
        Profiles.query
        .filter_by(company_id=company_id, role=UserRole.ADMIN)
        .first()
    )


def can_access_thread(profile: Profiles, company_id: int) -> bool:
    if profile.role == UserRole.SUPER_ADMIN:
        return True
    return profile.role == UserRole.ADMIN and profile.company_id == company_id


def thread_summary(company: Company, current_user_id: int):
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
    admin_profile = get_company_admin(company.id)
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


def unread_count_for_profile(user_id: int, profile: Profiles) -> int:
    query = ChatMessage.query.filter(
        ChatMessage.sender_id != user_id,
        ChatMessage.is_read.is_(False),
    )
    if profile.role == UserRole.ADMIN:
        if not profile.company_id:
            return 0
        query = query.filter(ChatMessage.company_id == profile.company_id)
    return query.count()
