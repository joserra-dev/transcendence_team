# --- ETAPA 1: CONSTRUCCIÓN ---
FROM python:3.12-slim AS builder

WORKDIR /app

# Dependencias del sistema necesarias para WeasyPrint
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libpango-1.0-0 \
    libpangoft2-1.0-0


# Como el Dockerfile está en la misma carpeta que requirements.txt:
COPY requirements.txt .
# Instalamos los requerimientos de forma global (SIN --user)
RUN pip install --no-cache-dir -r requirements.txt


# --- ETAPA 2: EJECUCIÓN (La imagen final ligera) ---
FROM python:3.12-slim AS runner

WORKDIR /app

# Dependencias del sistema necesarias para OpenCV en la imagen final
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    openssl \
    curl \
    && rm -rf /var/lib/apt/lists/*

# EL TRUCO CLAVE: Copiamos TODO el entorno de paquetes globales de Python y sus ejecutables
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiamos el código de la app
COPY . .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["sh","/app/entrypoint.sh"]