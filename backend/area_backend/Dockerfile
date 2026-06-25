# --- ETAPA 1: CONSTRUCCIÓN ---
FROM python:3.12-slim AS builder

WORKDIR /app

# Instalar herramientas de compilación que puedan hacer falta
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ && rm -rf /var/lib/apt/lists/*

# Instalar PyTorch CPU de forma global en el builder
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

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
    && rm -rf /var/lib/apt/lists/*

# EL TRUCO CLAVE: Copiamos TODO el entorno de paquetes globales de Python y sus ejecutables
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiamos el código de la app
COPY . .

CMD ["python", "app.py"]