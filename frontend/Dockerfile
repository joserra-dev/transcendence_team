# Etapa 1: Build de Angular
FROM node:20-alpine AS build-stage

WORKDIR /app

# Copiar el proyecto Angular
COPY camper/ .

# Instalar dependencias
RUN npm install

# Dar permisos de ejecución al CLI de Angular
RUN chmod +x node_modules/.bin/ng

# Compilar la app Angular en modo producción
RUN npx ng build --configuration=production

# Etapa 2: Servir con Nginx
FROM nginx:stable-alpine AS production-stage

RUN rm -rf /usr/share/nginx/html/*

COPY --from=build-stage /app/dist/camper/browser /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf

# Instalar envsubst
RUN apk add --no-cache gettext

# Copiar script de arranque
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/docker-entrypoint.sh"]
