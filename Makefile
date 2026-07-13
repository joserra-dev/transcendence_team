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
		echo "FLASK_ENV=development" > .env; \
		echo "FLASK_DEBUG=1" >> .env; \
		read -p "Puerto Front [4200]: " front; \
		front=$${front:-4200}; \
		echo "FRONT_PORT=$$front" >> .env; \
		echo "URL_FRONT=https://$(HOST):$$front" >> .env; \
		read -p "Puerto Back [8000]: " back; \
		back=$${back:-8000}; \
		echo "BACK_PORT=$$back" >> .env; \
		echo "URL_BACK=https://$(HOST):$$back" >> .env; \
		read -p "Puerto PostgreSQL [5432]: " db; \
		db=$${db:-5432}; \
		read -p "Password PostgreSQL: " pass; \
		read -p "Nombre DB [defaultdb]: " name; \
		name=$${name:-defaultdb}; \
		echo "POSTGRES_DB=$$name" >> .env; \
		echo "POSTGRES_USER=defaultdb_user" >> .env; \
		echo "POSTGRES_PASSWORD=$$pass" >> .env; \
		echo "POSTGRES_PORT=$$db" >> .env; \
		echo "DATABASE_URL=postgresql://defaultdb_user:$$pass@db:5432/$$name" >> .env; \
		echo "MAIL_SERVER=smtp.gmail.com" >> .env; \
		echo "MAIL_PORT=587" >> .env; \
		echo "MAIL_USE_TLS=True" >> .env; \
		read -p "MAIL_USERNAME: " user; \
		read -p "MAIL_PASSWORD: " mailpass; \
		read -p "MAIL_DEFAULT_SENDER: " sender; \
		echo "MAIL_USERNAME=$$user" >> .env; \
		echo "MAIL_PASSWORD=$$mailpass" >> .env; \
		echo "MAIL_DEFAULT_SENDER=$$sender" >> .env; \
		echo -e "$(COLOR_GREEN)✔ .env creado$(COLOR_RESET)"; \
	else \
		echo -e "$(COLOR_GREEN)✔ .env ya existe$(COLOR_RESET)"; \
	fi