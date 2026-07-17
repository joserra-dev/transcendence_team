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
    cert_ok=0
    if [ -f /app/certs/cert.pem ] && [ -f /app/certs/key.pem ]; then
        # Verifica que el par cert/key coincide y no está corrupto.
        if openssl x509 -in /app/certs/cert.pem -noout >/dev/null 2>&1 && \
           openssl rsa -in /app/certs/key.pem -check -noout >/dev/null 2>&1; then
            cert_ok=1
        else
            echo "ADVERTENCIA: los certificados existentes son inválidos o no coinciden. Regenerando."
        fi
    fi

    if [ "$cert_ok" -ne 1 ]; then
        echo "Generando certificado autofirmado de DESARROLLO (no válido para producción)."
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
