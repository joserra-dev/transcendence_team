from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_babel import gettext as _
from datetime import datetime

from database import db
from models.users import Users
from models.friend import Friend

friends_bp = Blueprint('friends_bp', __name__, url_prefix='/api/friends')


def _user_friend_dict(friend: Users):
    return {
        "id": friend.id,
        "email": friend.email,
        "nombrePersona": friend.profile.name if friend.profile else "",
        "apellidosPersona": friend.profile.last_name if friend.profile else "",
        "avatar": friend.profile.avatar if friend.profile else "",
        "role": friend.profile.role.value if friend.profile else "user",
    }


@friends_bp.route('', methods=['GET'])
@jwt_required()
def list_friends():
    current_user_id = get_jwt_identity()
    friendships = Friend.query.filter_by(user_id=current_user_id).all()
    friends = []
    for f in friendships:
        user = Users.query.get(f.friend_id)
        if user:
            friends.append(_user_friend_dict(user))
    return jsonify(friends), 200


@friends_bp.route('', methods=['POST'])
@jwt_required()
def add_friend():
    current_user_id = get_jwt_identity()
    data = request.get_json() or {}
    friend_id = data.get('friend_id')

    if not friend_id:
        return jsonify({"error": _("El identificador del usuario es obligatorio")}), 400

    if int(friend_id) == int(current_user_id):
        return jsonify({"error": _("No puedes agregarte a ti mismo")}), 400

    existing = Friend.query.filter_by(user_id=current_user_id, friend_id=friend_id).first()
    if existing:
        return jsonify({"error": _("Este usuario ya está en tu lista de amigos")}), 400

    friend = Users.query.get(friend_id)
    if not friend:
        return jsonify({"error": _("Usuario no encontrado")}), 404

    friendship = Friend(user_id=current_user_id, friend_id=friend_id, created_at=datetime.utcnow())
    db.session.add(friendship)
    db.session.commit()
    return jsonify({"mensaje": _("Amigo agregado correctamente"), "amigo": _user_friend_dict(friend)}), 201


@friends_bp.route('/<int:friend_id>', methods=['DELETE'])
@jwt_required()
def remove_friend(friend_id):
    current_user_id = get_jwt_identity()
    friendship = Friend.query.filter_by(user_id=current_user_id, friend_id=friend_id).first()
    if not friendship:
        return jsonify({"error": _("Este usuario no está en tu lista de amigos")}), 404

    db.session.delete(friendship)
    db.session.commit()
    return jsonify({"mensaje": _("Amigo eliminado correctamente")}), 200
