FROM postgres:18

# Copiamos los scripts de inicialización
COPY init /docker-entrypoint-initdb.d/

# Render y Postgres usan variables de entorno estándar:
# POSTGRES_DB
# POSTGRES_USER
# POSTGRES_PASSWORD
# POSTGRES_INITDB_ARGS (opcional)
