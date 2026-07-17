# ==========================================
# ETAPA DE DESARROLLO / BUILD
# ==========================================
FROM node:20-alpine AS development

WORKDIR /app

# Copiamos primero los ficheros de dependencias
COPY camper/package*.json ./
RUN npm install

# Copiamos el resto del proyecto Angular
COPY camper/ .

# Dar permisos al CLI
RUN chmod +x node_modules/.bin/ng

EXPOSE 4200

# ==========================================
# ETAPA DE PRODUCCIÓN (NGINX)
# ==========================================
FROM development AS build-stage
RUN npx ng build --configuration=production

FROM nginx:stable-alpine AS production
RUN rm -rf /usr/share/nginx/html/*

COPY --from=build-stage /app/dist/camper/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# IMPORTANTE (seguridad, CWE-295):
# No se embebe ningún certificado autofirmado en la imagen de producción.
# Los certificados TLS REALES (firmados por una CA de confianza) deben montarse
# en /etc/nginx/ssl/ como un volumen desde el host, p. ej.:
#   services.frontend.volumes:
#     - ./frontend/ssl:/etc/nginx/ssl:ro
# con los archivos nginx-selfsigned.crt / nginx-selfsigned.key (o los nombres que
# indique tu CA). Sin ellos, nginx NO arrancará en producción: eso es lo deseado
# para no exponer tráfico "HTTPS" con un certificado autofirmado inválido.
RUN apk add --no-cache openssl gettext && \
    mkdir -p /etc/nginx/ssl

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 443
ENTRYPOINT ["/docker-entrypoint.sh"]