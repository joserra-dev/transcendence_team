FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Como el Dockerfile está en la misma carpeta que requirements.txt:
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo lo que hay en esta carpeta (area_backend) a /app
COPY . .

CMD ["python", "app.py"]
