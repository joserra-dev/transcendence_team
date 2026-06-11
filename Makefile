# Colores para la terminal
COLOR_RESET  = \033[0m
COLOR_RED    = \033[31m
COLOR_GREEN  = \033[32m
COLOR_YELLOW = \033[33m
COLOR_BLUE   = \033[34m

# Detectar el hostname de forma automática
HOST := $(shell hostname)
HOST := $(if $(HOST),$(HOST),localhost)

# Comando por defecto
make: .env
	@echo "$(COLOR_BLUE)🐳 Levantando contenedores con docker-compose...$(COLOR_RESET)"
	docker-compose up --build

# Creación automática del .env
.env:
	@echo "$(COLOR_YELLOW)📝 Creando archivo .env por primera vez...$(COLOR_RESET)"
	@echo "$(COLOR_BLUE)🙋 Por favor, introduce los siguientes datos:$(COLOR_RESET)"
	@echo "FLASK_ENV=development" >> .env
	@echo "FLASK_DEBUG=1" >> .env
	@read -p "Introduce el puerto para el Front-end: " port; \
	echo "FRONT_PORT=$$port" >> .env; \
	echo "URL_FRONT=http://$(HOST):$$port" >> .env; \
	read -p "Introduce el puerto para el Back-end: " portback; \
	echo "BACK_PORT=$$portback" >> .env; \
	echo "URL_BACK=http://$(HOST):$$portback" >> .env
	
	
	@echo ""
	@echo "$(COLOR_BLUE)🐘 Configuración de conexión a PostgreSQL:$(COLOR_RESET)"
	@read -p "Host de la Base de Datos (ej. localhost o db): " db_host; \
	read -p "Puerto de Postgres (ej. 5432): " db_port; \
	read -p "Usuario de Postgres: " db_user; \
	read -p "Contraseña de Postgres: " db_pass; \
	read -p "Nombre de la Base de Datos: " db_name; \
	echo "DATABASE_URL=postgresql://$$db_user:$$db_pass@$$db_host:$$db_port/$$db_name" >> .env

	@echo ""
	@echo "$(COLOR_BLUE)📧 Configuración de Correo (Gmail SMTP):$(COLOR_RESET)"
	@echo "MAIL_SERVER=smtp.gmail.com" >> .env
	@echo "MAIL_PORT=587" >> .env
	@echo "MAIL_USE_TLS=True" >> .env
	@read -p "Tu correo de Gmail (MAIL_USERNAME): " mail_user; \
	read -p "Tu contraseña de aplicación de Gmail (MAIL_PASSWORD): " mail_pass; \
	read -p "Correo remitente por defecto (MAIL_DEFAULT_SENDER): " mail_sender; \
	echo "MAIL_USERNAME=$$mail_user" >> .env; \
	echo "MAIL_PASSWORD=$$mail_pass" >> .env; \
	echo "MAIL_DEFAULT_SENDER=$$mail_sender" >> .env
	@echo "$(COLOR_GREEN)✓ Configuración de correo guardada.$(COLOR_RESET)"
	
	@echo ""

	@echo "$(COLOR_GREEN)✅ Archivo .env creado con éxito con tu URL combinada.$(COLOR_RESET)"

# Tu regla de pruebas con colores
all:
	@echo "$(COLOR_BLUE)Iniciando el proceso de construcción...$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)✓ Compilación exitosa$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)Advertencia: El proceso tardó más de lo normal$(COLOR_RESET)"
	@echo "$(COLOR_RED)Error: Archivo no encontrado$(COLOR_RESET)"

.PHONY: all make
