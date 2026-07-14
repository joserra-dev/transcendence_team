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

RUN apk add --no-cache openssl gettext && \
    mkdir -p /etc/nginx/ssl && \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
      -keyout /etc/nginx/ssl/nginx-selfsigned.key \
      -out /etc/nginx/ssl/nginx-selfsigned.crt \
      -subj "/C=ES/ST=BasqueCountry/L=Urduliz/O=42Urduliz/CN=*.42urduliz.com"

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 443
ENTRYPOINT ["/docker-entrypoint.sh"]