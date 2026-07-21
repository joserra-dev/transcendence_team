# ==========================================
# ETAPA DE DESARROLLO
# ==========================================
FROM node:20-alpine AS development

WORKDIR /app

COPY camper/package*.json ./
RUN npm install

COPY camper/ .

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
    mkdir -p /etc/nginx/ssl

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 443
ENTRYPOINT ["/docker-entrypoint.sh"]