COLOR_RESET  = \033[0m
COLOR_RED    = \033[31m
COLOR_GREEN  = \033[32m
COLOR_YELLOW = \033[33m
COLOR_BLUE   = \033[34m
make:
	docker compose up --build

all:
	@echo "$(COLOR_BLUE)Iniciando el proceso de construcción...$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)✓ Compilación exitosa$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)Advertencia: El proceso tardó más de lo normal$(COLOR_RESET)"
	@echo "$(COLOR_RED)Error: Archivo no encontrado$(COLOR_RESET)"

.PHONY: all