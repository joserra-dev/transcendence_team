FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Dependencias del sistema necesarias para WeasyPrint
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libpango-1.0-0 \
    libpangoft2-1.0-0


# Como el Dockerfile está en la misma carpeta que requirements.txt:
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo lo que hay en esta carpeta (area_backend) a /app
COPY . .

CMD ["python", "app.py"]
