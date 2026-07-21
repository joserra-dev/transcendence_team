# --- ETAPA 1: CONSTRUCCIÓN (Compilación de dependencias Python) ---
FROM python:3.12-slim AS builder

WORKDIR /app

# Herramientas de compilación para librerías C/C++
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# 🚀 1. Instalar la versión ligera de PyTorch (CPU) para no descargar CUDA (~4.5GB menos)
RUN pip install --no-cache-dir \
    torch torchvision \
    --index-url https://download.pytorch.org/whl/cpu

# 2. Instalar el resto de dependencias desde requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# --- ETAPA 2: EJECUCIÓN (Imagen final ligera) ---
FROM python:3.12-slim AS runner

WORKDIR /app

# Librerías dinámicas del sistema (OpenCV, WeasyPrint, Healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias de Python y ejecutables compilados desde el builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["sh", "/app/entrypoint.sh"]