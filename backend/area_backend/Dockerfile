# --- ETAPA 1: CONSTRUCCIÓN ---
FROM python:3.12-slim AS builder

WORKDIR /app

# Instalar herramientas de compilación que puedan hacer falta
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
# Instalamos todo en una carpeta local llamadas 'wheels' o directamente en el site-packages
RUN pip install --user --no-cache-dir -r requirements.txt

# --- ETAPA 2: EJECUCIÓN (La imagen final) ---
FROM python:3.12-slim AS runner

WORKDIR /app

# Copiamos solo las librerías ya instaladas desde la etapa de compilación
COPY --from=builder /root/.local /root/.local
#COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Asegurar que Python vea las librerías copiadas
ENV PATH=/root/.local/bin:$PATH

# Copiamos el código de la app
COPY . .

CMD ["python", "app.py"]