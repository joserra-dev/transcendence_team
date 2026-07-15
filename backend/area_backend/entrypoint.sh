#!/bin/sh

# Si la variable MODE es "https", generamos certificados y arrancamos con SSL
if [ "$APP_MODE" = "https" ]; then
    echo "Iniciando en modo HTTPS (Seguro)..."
    mkdir -p /app/certs
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /app/certs/key.pem -out /app/certs/cert.pem \
        -subj '/C=ES/ST=State/L=City/O=Organization/CN=localhost'
    # Arrancamos Flask con certificados
    exec python -m flask run --host=0.0.0.0 --port=8000 --cert=/app/certs/cert.pem --key=/app/certs/key.pem
else
    echo "Iniciando en modo HTTP (Desarrollo)..."
    # Activamos el modo debug para desarrollo HTTP
    export FLASK_DEBUG=1
    # Arrancamos Flask normal
    exec python -m flask run --host=0.0.0.0 --port=8000
fi
