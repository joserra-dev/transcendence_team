from datetime import datetime, timezone

from flask import Blueprint, jsonify
from sqlalchemy import text

from database import db

status_bp = Blueprint('status_bp', __name__)


@status_bp.route('/status', methods=['GET'])
def get_status():
    try:
        db.session.execute(text('SELECT 1'))
        database = {"status": "ok"}
        database_status = 200
    except Exception as exc:
        database = {"status": "error", "error": str(exc)}
        database_status = 503

    status = {
        "service": "hemen-go",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "database": database,
    }
    return jsonify(status), database_status
