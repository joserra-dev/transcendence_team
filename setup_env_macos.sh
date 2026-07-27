#!/bin/bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_PREFIX="[SETUP]"

info()  { echo "$LOG_PREFIX \033[1;34mINFO\033[0m  $*"; }
ok()    { echo "$LOG_PREFIX \033[1;32mOK\033[0m    $*"; }
warn()  { echo "$LOG_PREFIX \033[1;33mWARN\033[0m  $*"; }
error() { echo "$LOG_PREFIX \033[1;31mERROR\033[0m $*"; }

# ==============================================================================
# Utilidades
# ==============================================================================

detect_platform() {
    if [[ "$(uname)" == "Darwin" ]]; then
        PLATFORM="macos"
        MACOS_VER="$(sw_vers -productVersion 2>/dev/null || echo 'unknown')"
        MACOS_BUILD="$(sw_vers -buildVersion 2>/dev/null || echo 'unknown')"
    else
        PLATFORM="unknown"
        warn "Este script esta disenado para macOS"
        return 1
    fi
}

check_cmd() {
    command -v "$1" >/dev/null 2>&1
}

install_pkg() {
    if ! check_cmd brew; then
        error "Homebrew no esta instalado. Instalalo primero desde https://brew.sh/"
        exit 1
    fi
    info "Instalando paquetes via Homebrew: $*"
    brew install "$@"
}

start_service_macos() {
    local svc="$1"
    if brew services list 2>/dev/null | grep -q "^$svc"; then
        brew services restart "$svc" 2>/dev/null || brew services start "$svc" 2>/dev/null || true
    else
        brew services start "$svc" 2>/dev/null || true
    fi
}

# ==============================================================================
# Docker (Colima en macOS)
# ==============================================================================

install_colima() {
    info "Instalando Colima..."
    install_pkg colima
    ok "Colima instalado"
}

start_colima() {
    info "Iniciando Colima..."
    colima start 2>/dev/null || {
        warn "No se pudo iniciar Colima. Intentando con configuracion predeterminada..."
        colima start --cpu 2 --memory 4 --disk 60 2>/dev/null || true
    }
    sleep 3
    if colima status 2>/dev/null | grep -q "Running"; then
        ok "Colima esta corriendo"
    else
        warn "Colima no esta corriendo"
    fi
}

check_colima() {
    if ! check_cmd colima; then
        warn "Colima no esta instalado"
        if [ "$CI" = "true" ] || [ ! -t 0 ]; then
            warn "La instalacion de Colima requiere interaccion (provisioning de VM)"
            warn "Instalalo manualmente: brew install colima && colima start"
        else
            install_colima
            start_colima
        fi
    fi

    if colima status 2>/dev/null | grep -q "Running"; then
        ok "Colima $(colima version 2>/dev/null | head -1 | awk '{print $2}') esta corriendo"
    else
        warn "Colima instalado pero no esta corriendo"
        start_colima
    fi

    if colima status 2>/dev/null | grep -q "Running"; then
        if [ -e /Applications/Docker.app ]; then
            if launchctl list 2>/dev/null | grep -q "com.docker.docker"; then
                warn "Docker Desktop y Colima detectados simultaneamente"
                warn "Ambos pueden entrar en conflicto por el socket Docker"
                info "Si tienes problemas, deten Docker Desktop con:"
                info "  brew services stop docker"
                info "  open -a Docker --unload"
            fi
        fi
    fi
}

install_docker() {
    warn "Docker Desktop no se instala automaticamente en macOS"
    info "Usa Colima como alternativa: brew install colima && colima start"
    info "Docker Desktop: https://www.docker.com/products/docker-desktop/"
    return 1
}

check_docker() {
    if ! check_cmd docker; then
        warn "Docker CLI no esta instalado"
        if ! install_colima; then
            error "Instala Docker manualmente en macOS. Opciones:"
            error "  - Colima: brew install colima && colima start"
            error "  - Docker Desktop: https://www.docker.com/products/docker-desktop/"
            exit 1
        fi
        if ! check_colima; then
            error "Colima no disponible. No se puede configurar Docker en macOS."
            exit 1
        fi
        if ! docker info >/dev/null 2>&1; then
            error "Docker CLI no funciona con Colima. Ejecuta: eval $(colima docker-env)"
            exit 1
        fi
        ok "Docker CLI funciona a traves de Colima"
        return
    fi

    if ! docker info >/dev/null 2>&1; then
        warn "El daemon de Docker no esta corriendo. Intentando iniciar..."
        if check_cmd colima; then
            start_colima
        fi
        if ! docker info >/dev/null 2>&1; then
            error "Docker esta instalado pero no se pudo iniciar el daemon. Iniciacarlo manualmente."
            exit 1
        fi
    fi
    ok "Docker $(docker --version | awk '{print $3}' | tr -d ','): $(docker info --format '{{.ServerVersion}}' 2>/dev/null || echo 'desconocida')"
}

# ==============================================================================
# Docker Compose
# ==============================================================================

check_docker_compose() {
    if check_cmd docker-compose; then
        COMPOSE_CMD="docker-compose"
        COMPOSE_VER="$(docker-compose --version | awk '{print $4}' | tr -d ',')"
    elif docker compose version >/dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
        COMPOSE_VER="$(docker compose version --short 2>/dev/null || echo 'desconocida')"
    elif check_cmd docker && docker compose version >/dev/null 2>&1; then
        COMPOSE_CMD="docker compose"
        COMPOSE_VER="$(docker compose version --short 2>/dev/null || echo 'desconocida')"
    else
        warn "Docker Compose plugin no detectado. Instalando..."
        brew install docker-compose 2>/dev/null || true
        if check_cmd docker-compose; then
            COMPOSE_CMD="docker-compose"
            COMPOSE_VER="$(docker-compose --version | awk '{print $4}' | tr -d ',')"
        elif docker compose version >/dev/null 2>&1; then
            COMPOSE_CMD="docker compose"
            COMPOSE_VER="$(docker compose version --short 2>/dev/null || echo 'desconocida')"
        else
            error "Docker Compose no esta disponible. Instalo desde https://docs.docker.com/compose/install/"
            exit 1
        fi
    fi
    ok "Docker Compose $COMPOSE_VER (usando: $COMPOSE_CMD)"
}

# ==============================================================================
# Python + pip
# ==============================================================================

install_python() {
    info "Instalando Python 3 y pip..."
    install_pkg python@3.12 python@3.11 python@3.10 python3
    ok "Python instalado"
}

check_python() {
    if ! check_cmd python3; then
        if ! check_cmd python; then
            warn "Python 3 no esta instalado"
            install_python || {
                error "Instala Python 3.10+ manualmente desde https://www.python.org/downloads/"
                exit 1
            }
        fi
    fi
    PYTHON_CMD="${PYTHON_CMD:-python3}"
    if ! check_cmd python3 && check_cmd python; then
        PYTHON_CMD="python"
    else
        PYTHON_CMD="python3"
    fi

    PYTHON_VER="$($PYTHON_CMD --version 2>&1 | awk '{print $2}')"
    PYTHON_MAJOR="$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')"
    PYTHON_MINOR="$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')"
    if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]; }; then
        warn "Python $PYTHON_VER detectado. Se recomienda Python 3.10+"
    else
        ok "Python $PYTHON_VER"
    fi

    if ! check_cmd pip3 && ! check_cmd pip; then
        warn "pip no encontrado, instalando..."
        brew install pip 2>/dev/null || true
    fi
    ok "pip disponible"
}

# ==============================================================================
# Node.js + npm
# ==============================================================================

install_node() {
    info "Instalando Node.js 20 LTS..."
    brew install node@20
    brew link --force --overwrite node@20 2>/dev/null || true
    ok "Node.js instalado"
}

check_node() {
    if ! check_cmd node; then
        warn "Node.js no esta instalado"
        install_node || {
            error "Instala Node.js 20+ manualmente desde https://nodejs.org/"
            exit 1
        }
    fi
    NODE_VER="$(node --version)"
    NODE_MAJOR="$(node -p 'process.versions.node.split(".")[0]')"
    npm_VER="$(npm --version)"
    if [ "$NODE_MAJOR" -lt 20 ]; then
        warn "Node $NODE_VER detectado. Se requiere Node.js 20+. Actualizando..."
        install_node || true
        NODE_VER="$(node --version)"
        NODE_MAJOR="$(node -p 'process.versions.node.split(".")[0]')"
        if [ "$NODE_MAJOR" -lt 20 ]; then
            warn "Node.js sigue siendo antiguo. Considera actualizar manualmente."
        fi
    else
        ok "Node.js $NODE_VER"
    fi

    if ! check_cmd npm; then
        warn "npm no encontrado junto a Node.js"
        install_node || true
    fi
    ok "npm $(npm --version)"
}

# ==============================================================================
# PostgreSQL local
# ==============================================================================

install_postgres() {
    info "Instalando PostgreSQL..."
    install_pkg postgresql
    start_service_macos postgresql
    ok "PostgreSQL instalado"
}

check_postgres_local() {
    if ! check_cmd psql; then
        warn "Cliente psql no disponible"
        install_postgres || {
            warn "PostgreSQL no instalado. Se usara el contenedor Docker 'db'."
            return
        }
    else
        ok "Cliente psql $(psql --version | awk '{print $3}') disponible"
    fi
    if ! check_cmd pg_isready; then
        warn "pg_isready no disponible, puede que PostgreSQL no este corriendo"
        start_service_macos postgresql
    fi
    if pg_isready -q; then
        ok "PostgreSQL server esta corriendo localmente"
    else
        warn "PostgreSQL server local no disponible. Se usara el contenedor Docker 'db'."
    fi
}

# ==============================================================================
# Redis local
# ==============================================================================

install_redis() {
    info "Instalando Redis..."
    install_pkg redis
    start_service_macos redis
    ok "Redis instalado"
}

check_redis_local() {
    if ! check_cmd redis-cli; then
        warn "redis-cli no disponible"
        install_redis || {
            warn "Redis no instalado. Se usara el contenedor Docker 'redis'."
            return
        }
    else
        ok "redis-cli disponible"
    fi
    if ! redis-cli ping >/dev/null 2>&1; then
        warn "Redis no esta corriendo localmente"
        start_service_macos redis
        sleep 1
        redis-cli ping >/dev/null 2>&1 && ok "Redis corriendo" || warn "Redis sigue sin responder. Se usara contenedor Docker."
    else
        ok "Redis corriendo localmente"
    fi
}

# ==============================================================================
# Angular CLI (opcional)
# ==============================================================================

install_angular_cli() {
    info "Instalando Angular CLI globalmente..."
    npm install -g @angular/cli || {
        warn "No se pudo instalar Angular CLI globalmente"
        return 1
    }
    ok "Angular CLI instalado"
}

check_angular_cli() {
    if ! check_cmd ng; then
        warn "Angular CLI no instalado"
        install_angular_cli || warn "Puedes usar 'npx ng serve' como alternativa."
    else
        ok "Angular CLI $(ng version 2>/dev/null | grep 'Angular CLI' | awk '{print $3}' || echo '?') disponible"
    fi
}

# ==============================================================================
# Variables de entorno
# ==============================================================================

check_env() {
    if [ -f "$SCRIPT_DIR/.env" ]; then
        ok ".env existe"
        if grep -q "^SUPER_ADMIN_PASSWORD=" "$SCRIPT_DIR/.env" 2>/dev/null; then
            ok "SUPER_ADMIN_PASSWORD definida en .env"
        else
            warn "SUPER_ADMIN_PASSWORD no definida en .env. Ejecuta 'make env' para generarla."
        fi
    elif [ -f "$SCRIPT_DIR/.env.example" ]; then
        warn ".env no existe, pero hay .env.example"
        info "  -> cp .env.example .env"
        info "  -> make env MODE=dev (o MODE=prod)"
    else
        warn "No se encontro ni .env ni .env.example"
        info "  -> Ejecuta 'make env' para generar .env interactivamente"
    fi
}

# ==============================================================================
# SSL
# ==============================================================================

check_ssl_certs() {
    if [ -d "$SCRIPT_DIR/frontend/ssl" ]; then
        if ls "$SCRIPT_DIR/frontend/ssl/"*.crt >/dev/null 2>&1 && ls "$SCRIPT_DIR/frontend/ssl/"*.key >/dev/null 2>&1; then
            ok "Certificados SSL locales encontrados en frontend/ssl/"
        else
            warn "Carpeta frontend/ssl/ existe pero no contiene certificados validos (.crt/.key)"
        fi
    else
        warn "Carpeta frontend/ssl/ no existe"
    fi
}

# ==============================================================================
# Git / Make
# ==============================================================================

check_git() {
    if check_cmd git; then
        ok "Git $(git --version | awk '{print $3}') disponible"
    else
        warn "Git no detectado. Instalando..."
        install_pkg git
    fi
}

check_make() {
    if check_cmd make; then
        ok "Make disponible"
    else
        warn "Make no detectado. Instalando..."
        install_pkg make
    fi
}

# ==============================================================================
# MAIN
# ==============================================================================

main() {
    detect_platform || exit 1
    info "=== Transcendence Team - Preparacion de entorno (macOS) ==="
    echo ""
    info "Platform: macOS $MACOS_VER (build $MACOS_BUILD)"
    echo ""

    if ! check_cmd brew; then
        error "Homebrew no esta instalado. Es necesario para macOS."
        info "  Instalo ejecutando:"
        info "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi

    check_make
    check_git
    check_docker
    check_docker_compose
    check_colima
    check_python
    check_node
    check_env
    check_postgres_local
    check_redis_local
    check_angular_cli
    check_ssl_certs

    echo ""
    ok "=== Verificacion completada ==="
    info "Para ejecutar el proyecto:"
    info "  - Desarrollo : make dev"
    info "  - Produccion : make prod"
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        info "  - Generar .env: make env MODE=dev  (o MODE=prod)"
    fi
}

main