#!/bin/sh

if [ ! -f /etc/nginx/ssl/nginx-selfsigned.crt ] || [ ! -f /etc/nginx/ssl/nginx-selfsigned.key ]; then
    echo "ADVERTENCIA: no se encontraron certificados TLS montados."
    echo "Generando certificado autofirmado de DESARROLLO..."
    mkdir -p /etc/nginx/ssl
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/nginx-selfsigned.key \
        -out /etc/nginx/ssl/nginx-selfsigned.crt \
        -subj "/C=ES/ST=BasqueCountry/L=Urduliz/O=42Urduliz/CN=localhost"
fi

# Reemplazar las variables de entorno en el template
if [ -f /usr/share/nginx/html/assets/env.template.js ]; then
    envsubst '${URL_FRONT} ${URL_BACK}' < /usr/share/nginx/html/assets/env.template.js > /usr/share/nginx/html/assets/env.js
fi

exec nginx -g "daemon off;"