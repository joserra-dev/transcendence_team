# ==============================================================================
# CONFIGURATION AND VARIABLES
# ==============================================================================

COLOR_RESET  = \033[0m
COLOR_RED    = \033[31m
COLOR_GREEN  = \033[32m
COLOR_YELLOW = \033[33m
COLOR_BLUE   = \033[34m

# Detect operating system & stable host detection
OS := $(shell uname -s)
ifeq ($(OS), Darwin)
    HOST := localhost
else
    DETECTED_HOST := $(shell hostname)
    HOST := $(if $(DETECTED_HOST),$(DETECTED_HOST),localhost)
endif

.PHONY: all dev prod up up-prod clean fclean env

.DEFAULT_GOAL := help

# Asegura que las ejecuciones de scripts internos usen Bash compatible con 'read'
SHELL := /bin/bash

# ==============================================================================
# AVAILABLE COMMANDS (HELP)
# ==============================================================================

help:
	@echo -e "$(COLOR_BLUE)🐳 COMANDOS DISPONIBLES EN ESTE PROYECTO:$(COLOR_RESET)"
	@echo "=================================================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_GREEN)make %-15s$(COLOR_RESET) %s\n", $$1, $$2}'
	@echo -e "=================================================================="

# ==============================================================================
# MAIN RULES
# ==============================================================================

all: dev ## Default: Inicializa el entorno e inicia en MODO DESARROLLO (Hot-Reload)

dev: env up ## Inicializa y arranca en MODO DESARROLLO (Para Debuggear Front/Back)

prod: env up-prod ## Inicializa y arranca en MODO PRODUCCIÓN (Nginx optimizado)

up: ## Levantar contenedores en MODO DESARROLLO
	@echo -e "$(COLOR_BLUE)🐳 Levantando entorno de DESARROLLO (Modo Debug)...$(COLOR_RESET)"
	docker-compose up -d --build --remove-orphans
	@echo -e "$(COLOR_GREEN)🚀 ¡Entorno de desarrollo corriendo con éxito! Front listo en su puerto asignado.$(COLOR_RESET)"

up-prod: ## Levantar contenedores en MODO PRODUCCIÓN
	@echo -e "$(COLOR_BLUE)🐳 Compilando y levantando entorno de PRODUCCIÓN (Nginx)...$(COLOR_RESET)"
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build --remove-orphans
	@echo -e "$(COLOR_GREEN)🚀 ¡Entorno de producción corriendo con éxito!$(COLOR_RESET)"

clean: ## Detiene contenedores sin perder datos ni imágenes
	@echo -e "$(COLOR_YELLOW)🛑 Deteniendo y limpiando contenedores activos...$(COLOR_RESET)"
	docker-compose down
	@echo -e "$(COLOR_GREEN)✓ Contenedores limpios.$(COLOR_RESET)"

fclean: ## Limpieza profunda total: Elimina contenedores, volúmenes, imágenes, huérfanos y .env
	@echo -e "$(COLOR_RED)🚨 LIMPIEZA PROFUNDA: Eliminando contenedores, volúmenes, huérfanos e imágenes...$(COLOR_RESET)"
	
	@# 1. Apagar contenedores, borrar volúmenes e imágenes creadas por el compose, incluyendo huérfanos del proyecto
	docker compose -f docker-compose.yml -f docker-compose.prod.yml down --rmi all --volumes --remove-orphans || true
	
	@# 2. EL TRUCO FINAL PARA HUÉRFANOS: Borra cualquier contenedor, red o volumen colgado/huérfano en todo el sistema Docker
	docker system prune -a --volumes -f || true
	
	@# 3. Limpieza de la caché interna de construcción de BuildKit
	docker builder prune -a -f || true
	
	@# 4. Eliminar el archivo de variables de entorno si existe
	@if [ -f .env ]; then \
		rm .env; \
		echo -e "$(COLOR_RED)🗑️ Archivo .env eliminado.$(COLOR_RESET)"; \
	fi
	@echo -e "$(COLOR_GREEN)💥 Todo el entorno (incluyendo huérfanos y cachés) ha sido reseteado desde cero.$(COLOR_RESET)"

# ==============================================================================
# AUTOMATIC ENVIRONMENT GENERATION (.env)
# ==============================================================================

env:
	@if [ ! -f .env ]; then \
		echo -e "$(COLOR_YELLOW)📝 Creando archivo .env por primera vez...$(COLOR_RESET)"; \
		echo -e "$(COLOR_BLUE)🙋 Por favor, introduce los siguientes datos:$(COLOR_RESET)"; \
		echo "FLASK_ENV=development" > .env; \
		echo "FLASK_DEBUG=1" >> .env; \
		read -p "Introduce el puerto para el Front-end (ej. 4200): " port; \
		echo "FRONT_PORT=$$port" >> .env; \
		echo "URL_FRONT=http://$(HOST):$$port" >> .env; \
		read -p "Introduce el puerto para el Back-end (ej. 8000): " portback; \
		echo "BACK_PORT=$$portback" >> .env; \
		echo "URL_BACK=http://$(HOST):$$portback" >> .env; \
		\
		echo ""; \
		echo -e "$(COLOR_BLUE)🐘 Configuración de conexión a PostgreSQL:$(COLOR_RESET)"; \
		read -p "Puerto de Postgres (ej. 5432): " db_port; \
		read -p "Contraseña de Postgres: " db_pass; echo ""; \
		read -p "Nombre de la Base de Datos (ej. defaultdb): " db_name; \
		echo "POSTGRES_DB=$$db_name" >> .env;\
		echo "POSTGRES_USER=defaultdb_user" >> .env;\
		echo "POSTGRES_PASSWORD=$$db_pass" >> .env;\
		echo "POSTGRES_PORT=$$db_port" >> .env;\
		echo "DATABASE_URL=postgresql://defaultdb_user:$$db_pass@db:$$db_port/$$db_name" >> .env; \
		\
		echo ""; \
		echo -e "$(COLOR_BLUE)📧 Configuración de Correo (Gmail SMTP):$(COLOR_RESET)"; \
		echo "MAIL_SERVER=smtp.gmail.com" >> .env; \
		echo "MAIL_PORT=587" >> .env; \
		echo "MAIL_USE_TLS=True" >> .env; \
		read -p "Tu correo de Gmail (MAIL_USERNAME): " mail_user; \
		read -p "Tu contraseña de aplicaci710c77922dd5ón de Gmail (MAIL_PASSWORD): " mail_pass; echo ""; \
		read -p "Correo remitente por defecto (MAIL_DEFAULT_SENDER): " mail_sender; \
		echo "MAIL_USERNAME=$$mail_user" >> .env; \
		echo "MAIL_PASSWORD=$$mail_pass" >> .env; \
		echo "MAIL_DEFAULT_SENDER=$$mail_sender" >> .env; \
		echo -e "$(COLOR_GREEN)✓ Configuración de correo guardada.$(COLOR_RESET)"; \
		echo ""; \
		echo -e "$(COLOR_GREEN)✅ Archivo .env creado con éxito con tu URL combinada y configuraciones.$(COLOR_RESET)"; \
	else \
		echo -e "$(COLOR_GREEN)✔ El archivo .env ya existe. Saltando configuración interactiva.$(COLOR_RESET)"; \
	fi