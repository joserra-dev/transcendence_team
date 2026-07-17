#!/bin/sh

# HTTPS si BACK_SCHEME=https (prod via .env) o APP_MODE=https (compat).
if [ "${BACK_SCHEME}" = "https" ] || [ "$APP_MODE" = "https" ]; then
    echo "Iniciando en modo HTTPS (Seguro)..."
    mkdir -p /app/certs

    # Si ya se montaron certificados reales (CA de confianza) en /app/certs,
    # úsalos. En caso contrario se genera un certificado autofirmado de
    # DESARROLLO (CN=localhost) que NO es válido para producción real: el
    # tráfico no será de confianza para el cliente y nginx debe configurar
    # proxy_ssl_verify en consecuencia.
    if [ ! -f /app/certs/cert.pem ] || [ ! -f /app/certs/key.pem ]; then
        echo "ADVERTENCIA: no se encontraron certificados TLS montados. " \
             "Generando certificado autofirmado de DESARROLLO (no válido para producción)."
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout /app/certs/key.pem -out /app/certs/cert.pem \
            -subj '/C=ES/ST=State/L=City/O=Organization/CN=localhost'
    fi

    export APP_MODE=https
    exec python run.py
else
    echo "Iniciando en modo HTTP (Desarrollo)..."
    export FLASK_DEBUG=1
    exec python run.py
fi
