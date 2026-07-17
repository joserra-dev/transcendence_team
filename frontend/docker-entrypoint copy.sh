#!/bin/sh

# Reemplazar las variables de entorno en el template dentro de la carpeta assets
envsubst '${URL_FRONT} ${URL_BACK}' < /usr/share/nginx/html/assets/env.template.js > /usr/share/nginx/html/assets/env.js

# Ejecutar Nginx en primer plano
exec nginx -g "daemon off;"