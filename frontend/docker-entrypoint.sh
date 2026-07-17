#!/bin/sh

# Generar certificado TLS autofirmado de DESARROLLO si no se montaron certs
# reales (CA de confianza) en /etc/nginx/ssl. Para producción real, monta
# ./frontend/ssl:/etc/nginx/ssl:ro con tu certificado firmado por una CA.
if [ ! -f /etc/nginx/ssl/nginx-selfsigned.crt ] || [ ! -f /etc/nginx/ssl/nginx-selfsigned.key ]; then
    echo "ADVERTENCIA: no se encontraron certificados TLS montados. " \
         "Generando certificado autofirmado de DESARROLLO (no válido para producción)."
    mkdir -p /etc/nginx/ssl
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/nginx-selfsigned.key \
        -out /etc/nginx/ssl/nginx-selfsigned.crt \
        -subj "/C=ES/ST=BasqueCountry/L=Urduliz/O=42Urduliz/CN=localhost"
fi

# Reemplazar las variables de entorno en el template dentro de la carpeta assets
envsubst '${URL_FRONT} ${URL_BACK}' < /usr/share/nginx/html/assets/env.template.js > /usr/share/nginx/html/assets/env.js

# Ejecutar Nginx en primer plano
exec nginx -g "daemon off;"
