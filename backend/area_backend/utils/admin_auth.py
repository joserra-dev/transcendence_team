from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from models.users import UserRole, Users


def get_auth_user_and_profile():
    user_id = get_jwt_identity()
    user = Users.query.get(int(user_id))
    if not user or not user.profile:
        return None, None
    return user, user.profile


def require_admin(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user, profile = get_auth_user_and_profile()
        if not profile or profile.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
            return jsonify({"error": "No autorizado"}), 403
        return fn(user, profile, *args, **kwargs)

    return wrapper


def require_super_admin(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user, profile = get_auth_user_and_profile()
        if not profile or profile.role != UserRole.SUPER_ADMIN:
            return jsonify({"error": "Se requiere rol de superadministrador"}), 403
        return fn(user, profile, *args, **kwargs)

    return wrapper
