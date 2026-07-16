import os

import eventlet

eventlet.monkey_patch()

from app import app  # noqa: E402
from socketio_ext import socketio  # noqa: E402


def _debug_enabled() -> bool:
    return os.getenv('FLASK_DEBUG', '0').strip().lower() in ('1', 'true')


if __name__ == '__main__':
    debug = _debug_enabled()

    if os.getenv('APP_MODE') == 'https':
        socketio.run(
            app,
            host='0.0.0.0',
            port=8000,
            certfile='/app/certs/cert.pem',
            keyfile='/app/certs/key.pem',
            debug=debug,
        )
    else:
        socketio.run(app, host='0.0.0.0', port=8000, debug=debug)
