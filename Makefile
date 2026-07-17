# ==============================================================================
# CONFIGURATION
# ==============================================================================

COLOR_RESET  = \033[0m
COLOR_RED    = \033[31m
COLOR_GREEN  = \033[32m
COLOR_YELLOW = \033[33m
COLOR_BLUE   = \033[34m

SHELL := /bin/bash

.DEFAULT_GOAL := help

.PHONY: all dev prod up up-prod clean fclean env doctor help status logs


# ==============================================================================
# SYSTEM DETECTION
# ==============================================================================

OS := $(shell uname -s)

ifeq ($(OS),Darwin)
    HOST := localhost
else
    HOST := $(shell hostname)
endif


# ==============================================================================
# DOCKER COMPOSE DETECTION
# ==============================================================================

ifeq ($(shell command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1 && echo yes),yes)

    COMPOSE=docker compose

else ifeq ($(shell command -v docker-compose >/dev/null 2>&1 && echo yes),yes)

    COMPOSE=docker-compose

else

    $(error Docker Compose no encontrado)

endif
# ==============================================================================
# STATUS AND LOGS
# ==============================================================================
status:
	@docker ps

logs: ## Ver logs del entorno de desarrollo
	@$(COMPOSE) \
	-f docker-compose.yml \
	-f docker-compose.dev.yml \
	logs -f


# ==============================================================================
# HELP
# ==============================================================================

help:
	@echo -e "$(COLOR_BLUE)"
	@echo "🐳 TRANSCENDENCE DOCKER COMMANDS"
	@echo "================================"
	@echo -e "$(COLOR_RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS=":.*?## "}; {printf "  $(COLOR_GREEN)%-15s$(COLOR_RESET) %s\n", $$1,$$2}'


# ==============================================================================
# MAIN COMMANDS
# ==============================================================================

all: prod ## Arranque por defecto en producción


dev: env up ## Entorno desarrollo


prod: env up-prod ## Entorno producción HTTPS/Nginx



# ==============================================================================
# START DEVELOPMENT
# ==============================================================================

up: ## Levantar desarrollo
	@echo -e "$(COLOR_BLUE)🐳 Arrancando desarrollo...$(COLOR_RESET)"
	$(COMPOSE) \
		-f docker-compose.yml \
		-f docker-compose.dev.yml \
		up -d --build --remove-orphans
	@echo -e "$(COLOR_GREEN)✔ Desarrollo levantado$(COLOR_RESET)"



# ==============================================================================
# START PRODUCTION
# ==============================================================================

up-prod: ## Levantar producción
	@echo -e "$(COLOR_BLUE)🐳 Arrancando producción...$(COLOR_RESET)"
	$(COMPOSE) \
		-f docker-compose.yml \
		-f docker-compose.prod.yml \
		up -d --build --remove-orphans
	@echo -e "$(COLOR_GREEN)✔ Producción levantada$(COLOR_RESET)"



# ==============================================================================
# DOCKER DOCTOR
# ==============================================================================

doctor: ## Diagnóstico del entorno
	@echo -e "$(COLOR_BLUE)"
	@echo "🩺 Docker Doctor"
	@echo "==============="
	@echo -e "$(COLOR_RESET)"
	@echo "Sistema: $(OS)"
	@echo "Host: $(HOST)"
	@echo ""
	@echo "Docker:"
	@if command -v docker >/dev/null 2>&1; then \
		echo -e "$(COLOR_GREEN)✔ Docker encontrado$(COLOR_RESET)"; \
	else \
		echo -e "$(COLOR_RED)✘ Docker no encontrado$(COLOR_RESET)"; \
	fi
	@echo ""
	@echo "Daemon:"
	@if docker info >/dev/null 2>&1; then \
		echo -e "$(COLOR_GREEN)✔ Docker funcionando$(COLOR_RESET)"; \
	else \
		echo -e "$(COLOR_RED)✘ Docker daemon parado$(COLOR_RESET)"; \
	fi
	@echo ""
	@echo "Compose:"
	@$(COMPOSE) version
	@echo ""
	@echo "Puertos:"
	@for port in 4200 443 5432 8000; do \
		if lsof -i :$$port >/dev/null 2>&1; then \
			echo -e "$(COLOR_YELLOW)⚠ Puerto $$port ocupado$(COLOR_RESET)"; \
			lsof -i :$$port | tail -1; \
		else \
			echo -e "$(COLOR_GREEN)✔ Puerto $$port libre$(COLOR_RESET)"; \
		fi; \
	done



# ==============================================================================
# CLEAN
# ==============================================================================

clean: ## Parar contenedores
	@echo -e "$(COLOR_YELLOW)🛑 Parando contenedores...$(COLOR_RESET)"
	$(COMPOSE) \
		-f docker-compose.yml \
		-f docker-compose.dev.yml \
		down
	@echo -e "$(COLOR_GREEN)✔ Limpieza realizada$(COLOR_RESET)"



fclean: ## Limpieza total Docker
	@echo -e "$(COLOR_RED)"
	@echo "🚨 LIMPIEZA COMPLETA"
	@echo -e "$(COLOR_RESET)"
	$(COMPOSE) \
		-f docker-compose.yml \
		-f docker-compose.dev.yml \
		-f docker-compose.prod.yml \
		down \
		--rmi all \
		--volumes \
		--remove-orphans || true
	docker system prune -af --volumes || true
	docker builder prune -af || true
	@if [ -f .env ]; then \
		rm .env; \
		echo "✔ .env eliminado"; \
	fi



# ==============================================================================
# ENVIRONMENT GENERATION
# ==============================================================================

env:
	@if [ ! -f .env ]; then \
		echo -e "$(COLOR_YELLOW)Creando .env$(COLOR_RESET)"; \
		read -p "Modo de entorno (dev/prod) [dev]: " mode; \
		mode=$${mode:-dev}; \
		if [ "$$mode" = "prod" ]; then \
			echo "FLASK_ENV=production" > .env; \
			echo "FLASK_DEBUG=0" >> .env; \
			echo "BACK_SCHEME=https" >> .env; \
			proto="https"; \
			front_base=8443; \
			back_base=8000; \
			host_env="$(HOST)"; \
		else \
			echo "FLASK_ENV=development" > .env; \
			echo "FLASK_DEBUG=1" >> .env; \
			echo "BACK_SCHEME=http" >> .env; \
			proto="http"; \
			front_base=4200; \
			back_base=8000; \
			host_env="localhost"; \
		fi; \
		find_free_port() { \
			p=$$1; \
			while lsof -i :$$p >/dev/null 2>&1; do p=$$((p+1)); done; \
			echo $$p; \
		}; \
		front=$$(find_free_port $$front_base); \
		echo "FRONT_PORT=$$front" >> .env; \
		echo "URL_FRONT=$$proto://$(HOST):$$front" >> .env; \
		echo -e "$(COLOR_GREEN)✔ Puerto Front asignado: $$front (libre desde $$front_base)$(COLOR_RESET)"; \
		back=$$(find_free_port $$back_base); \
		echo "BACK_PORT=$$back" >> .env; \
		echo "URL_BACK=$$proto://$(HOST):$$back" >> .env; \
		echo -e "$(COLOR_GREEN)✔ Puerto Back asignado: $$back (libre desde $$back_base)$(COLOR_RESET)"; \
		db=$$(find_free_port 5432); \
		jwt_secret=$$(python3 -c 'import secrets; print(secrets.token_hex(32))'); \
		echo "JWT_SECRET_KEY=$$jwt_secret" >> .env; \
		echo -e "$(COLOR_GREEN)✔ JWT_SECRET_KEY generada automáticamente$(COLOR_RESET)"; \
		echo "JWT_ACCESS_TOKEN_EXPIRES=120" >> .env; \
		public_api_key=$$(python3 -c 'import secrets; print(secrets.token_hex(32))'); \
		echo "PUBLIC_API_KEY=$$public_api_key" >> .env; \
		echo "PUBLIC_API_RATE_LIMIT=60" >> .env; \
		echo "RATELIMIT_STORAGE_URI=redis://redis:6379/0" >> .env; \
		echo -e "$(COLOR_GREEN)✔ PUBLIC_API_KEY generada automáticamente$(COLOR_RESET)"; \
		read -p "Password PostgreSQL: " pass; \
		read -p "Nombre DB [defaultdb]: " name; \
		name=$${name:-defaultdb}; \
		echo "POSTGRES_DB=$$name" >> .env; \
		echo "POSTGRES_USER=defaultdb_user" >> .env; \
		echo "POSTGRES_PASSWORD=$$pass" >> .env; \
		echo "POSTGRES_PORT=$$db" >> .env; \
		echo "DATABASE_URL=postgresql://defaultdb_user:$$pass@db:$$db/$$name" >> .env; \
		echo -e "$(COLOR_GREEN)✔ Puerto PostgreSQL asignado: $$db (libre desde 5432)$(COLOR_RESET)"; \
		read -p "Stripe Key [sk_test_...]: " stripe; \
		echo "STRIPE_KEY=$$stripe" >> .env; \
		echo "MAIL_SERVER=smtp.gmail.com" >> .env; \
		echo "MAIL_PORT=587" >> .env; \
		echo "MAIL_USE_TLS=True" >> .env; \
		read -p "MAIL_USERNAME: " user; \
		read -p "MAIL_DEFAULT_SENDER: " sender; \
		read -p "MAIL_PASSWORD: " mailpass; \
		echo "MAIL_USERNAME=$$user" >> .env; \
		echo "MAIL_PASSWORD=$$mailpass" >> .env; \
		echo "MAIL_DEFAULT_SENDER=$$sender" >> .env; \
		echo -e "$(COLOR_GREEN)✔ .env creado con éxito ($$proto)$(COLOR_RESET)"; \
	else \
		echo -e "$(COLOR_GREEN)✔ .env ya existe$(COLOR_RESET)"; \
	fi; \
	echo -e "$(COLOR_BLUE)🔐 Generando certificado TLS local para el frontend...$(COLOR_RESET)"; \
	if [ -x frontend/ssl/generate-local.sh ]; then \
		sh frontend/ssl/generate-local.sh $(HOST) || echo -e "$(COLOR_YELLOW)⚠ No se pudo generar el certificado local (¿openssl instalado?)$(COLOR_RESET)"; \
	else \
		echo -e "$(COLOR_YELLOW)⚠ No se encontró frontend/ssl/generate-local.sh$(COLOR_RESET)"; \
	fi
