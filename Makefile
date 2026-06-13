# ==============================================================================
# CONFIGURATION AND VARIABLES
# ==============================================================================

# Terminal colors
COLOR_RESET  = \033[0m
COLOR_RED    = \033[31m
COLOR_GREEN  = \033[32m
COLOR_YELLOW = \033[33m
COLOR_BLUE   = \033[34m

# Automatically detect host
HOST := $(shell hostname)
HOST := $(if $(HOST),$(HOST),localhost)

# Declare rules that are not physical files
.PHONY: all up clean rclean env


# Default rule executed when you just type 'make'
.DEFAULT_GOAL := help

# ==============================================================================
# AVAILABLE COMMANDS (HELP)
# ==============================================================================

help:
	@echo "$(COLOR_BLUE)🐳 COMANDOS DISPONIBLES EN ESTE PROYECTO:$(COLOR_RESET)"
	@echo "=================================================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_GREEN)make %-15s$(COLOR_RESET) %s\n", $$1, $$2}'
	@echo "=================================================================="

# ==============================================================================
# MAIN RULES
# ==============================================================================

# 1. MAKE ALL: Default command. Creates environment if missing and starts up.
all: env up ## MAKE ALL: Default command. Creates environment if missing and starts up.

# 2. MAKE UP: Smart startup. If images exist, it just starts them.
up: ## MAKE UP: Smart startup. If images exist, it just starts them.
	@echo "$(COLOR_BLUE)🐳 Comprobando imágenes locales y levantando contenedores...$(COLOR_RESET)"
	docker-compose up -d
	@echo "$(COLOR_GREEN)🚀 ¡Entorno corriendo con éxito!$(COLOR_RESET)"

# 3. MAKE CLEAN: Stops and removes active containers without losing data or images.
clean: ## MAKE CLEAN: Stops and removes active containers without losing data or images.
	@echo "$(COLOR_YELLOW)🛑 Deteniendo y limpiando contenedores activos...$(COLOR_RESET)"
	docker-compose down
	@echo "$(COLOR_GREEN)✓ Contenedores limpios.$(COLOR_RESET)"

# 4. MAKE RCLEAN: Deep clean. Removes containers, volumes, images, and the .env file.
rclean: ## MAKE RCLEAN: Deep clean. Removes containers, volumes, images, and the .env file.
	@echo "$(COLOR_RED)🚨 LIMPIEZA PROFUNDA: Eliminando contenedores, volúmenes e imágenes...$(COLOR_RESET)"
	docker-compose down --rmi all --volumes --remove-orphans
	@if [ -f .env ]; then \
		rm .env; \
		echo "$(COLOR_RED)🗑️ Archivo .env eliminado.$(COLOR_RESET)"; \
	fi
	@echo "$(COLOR_GREEN)💥 Todo el entorno ha sido reseteado desde cero.$(COLOR_RESET)"

# ==============================================================================
# AUTOMATIC ENVIRONMENT GENERATION (.env)
# ==============================================================================

# Interactive wizard to generate .env if it does not exist
env:
	@if [ ! -f .env ]; then \
		echo "$(COLOR_YELLOW)📝 Creando archivo .env por primera vez...$(COLOR_RESET)"; \
		echo "$(COLOR_BLUE)🙋 Por favor, introduce los siguientes datos:$(COLOR_RESET)"; \
		echo "FLASK_ENV=development" > .env; \
		echo "FLASK_DEBUG=1" >> .env; \
		read -p "Introduce el puerto para el Front-end (ej. 4200): " port; \
		echo "FRONT_PORT=$$port" >> .env; \
		echo "URL_FRONT=http://localhost:$$port" >> .env; \
		read -p "Introduce el puerto para el Back-end (ej. 5000): " portback; \
		echo "BACK_PORT=$$portback" >> .env; \
		echo "URL_BACK=http://localhost:$$portback" >> .env; \
		\
		echo ""; \
		echo "$(COLOR_BLUE)🐘 Configuración de conexión a PostgreSQL:$(COLOR_RESET)"; \
		read -p "Puerto de Postgres (ej. 5432): " db_port; \
		read -p "Usuario de Postgres (ej. defaultdb_user): " db_user; \
		read -p "Contraseña de Postgres: " db_pass; echo ""; \
		read -p "Nombre de la Base de Datos (ej. defaultdb): " db_name; \
		echo "POSTGRES_DB=$$db_name" >> .env;\
		echo "POSTGRES_USER=$$db_user" >> .env;\
		echo "POSTGRES_PASSWORD=$$db_pass" >> .env;\
		echo "DATABASE_URL=postgresql://$$db_user:$$db_pass@db:$$db_port/$$db_name" >> .env; \
		\
		echo ""; \
		echo "$(COLOR_BLUE)📧 Configuración de Correo (Gmail SMTP):$(COLOR_RESET)"; \
		echo "MAIL_SERVER=smtp.gmail.com" >> .env; \
		echo "MAIL_PORT=587" >> .env; \
		echo "MAIL_USE_TLS=True" >> .env; \
		read -p "Tu correo de Gmail (MAIL_USERNAME): " mail_user; \
		read -p "Tu contraseña de aplicación de Gmail (MAIL_PASSWORD): " mail_pass; echo ""; \
		read -p "Correo remitente por defecto (MAIL_DEFAULT_SENDER): " mail_sender; \
		echo "MAIL_USERNAME=$$mail_user" >> .env; \
		echo "MAIL_PASSWORD=$$mail_pass" >> .env; \
		echo "MAIL_DEFAULT_SENDER=$$mail_sender" >> .env; \
		echo "$(COLOR_GREEN)✓ Configuración de correo guardada.$(COLOR_RESET)"; \
		echo ""; \
		echo "$(COLOR_GREEN)✅ Archivo .env creado con éxito con tu URL combinada y configuraciones.$(COLOR_RESET)"; \
	else \
		echo "$(COLOR_GREEN)✔ El archivo .env ya existe. Saltando configuración interactiva.$(COLOR_RESET)"; \
	fi