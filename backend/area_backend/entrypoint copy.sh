#!/bin/sh

# HTTPS si BACK_SCHEME=https (prod via .env) o APP_MODE=https (compat).
if [ "${BACK_SCHEME}" = "https" ] || [ "$APP_MODE" = "https" ]; then
    echo "Iniciando en modo HTTPS (Seguro)..."
    mkdir -p /app/certs
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /app/certs/key.pem -out /app/certs/cert.pem \
        -subj '/C=ES/ST=State/L=City/O=Organization/CN=localhost'
    export APP_MODE=https
    exec python run.py
else
    echo "Iniciando en modo HTTP (Desarrollo)..."
    export FLASK_DEBUG=1
    exec python run.py
fi
