from flask_socketio import SocketIO

socketio = SocketIO(
    cors_allowed_origins='*',
    async_mode='threading',
    manage_session=False,
    path='/socket.io',
)


def init_realtime(app):
    socketio.init_app(app)
    import routes.chat_socket  # noqa: F401
    return socketio
