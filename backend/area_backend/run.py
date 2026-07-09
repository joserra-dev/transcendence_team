import os

from app import app, socketio

if __name__ == '__main__':
    debug_env = os.getenv('FLASK_DEBUG', 'False').strip().lower()
    modo_debug = debug_env in ['true', '1']
    cert = '/app/certs/cert.pem'
    key = '/app/certs/key.pem'

    socketio.run(
        app,
        host='0.0.0.0',
        port=8000,
        debug=modo_debug,
        ssl_context=(cert, key),
        allow_unsafe_werkzeug=True,
    )
