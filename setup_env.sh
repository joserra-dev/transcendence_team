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

detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO="$ID"
        PRETTY_NAME="$PRETTY_NAME"
    else
        error "/etc/os-release no encontrado"
        exit 1
    fi
}

check_cmd() {
    command -v "$1" >/dev/null 2>&1
}

install_pkg() {
    if [ "$DISTRO" = "ubuntu" ] || [ "$DISTRO" = "debian" ]; then
        info "Instalando paquetes: $*"
        sudo apt-get update -qq
        sudo apt-get install -y -qq "$@"
    else
        warn "Distro no soportada para instalación automática de paquetes ($DISTRO)"
        return 1
    fi
}

start_service() {
    local svc="$1"
    if check_cmd systemctl; then
        sudo systemctl enable -q "$svc" 2>/dev/null || true
        sudo systemctl start -q "$svc" 2>/dev/null || true
    elif check_cmd service; then
        sudo service "$svc" start 2>/dev/null || true
    fi
}

# ==============================================================================
# Docker
# ==============================================================================

install_docker() {
    info "Instalando Docker..."
    install_pkg ca-certificates curl gnupg lsb-release
    
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg 2>/dev/null || {
        warn "No se pudo añadir la clave GPG de Docker"
        return 1
    }
    
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
    
    sudo apt-get update -qq
    sudo apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    start_service docker
    ok "Docker instalado"
}

check_docker() {
    if ! check_cmd docker; then
        warn "Docker no está instalado"
        if ! install_docker; then
            error "Instala Docker manualmente desde https://docs.docker.com/get-docker/"
            exit 1
        fi
    fi
    if ! docker info >/dev/null 2>&1; then
        warn "El daemon de Docker no está corriendo. Intentando iniciar..."
        start_service docker
        sleep 3
        if ! docker info >/dev/null 2>&1; then
            error "Docker está instalado pero no se pudo iniciar el daemon. Inícialo manualmente."
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
        install_docker || true
        sleep 2
        if check_cmd docker-compose; then
            COMPOSE_CMD="docker-compose"
            COMPOSE_VER="$(docker-compose --version | awk '{print $4}' | tr -d ',')"
        elif docker compose version >/dev/null 2>&1; then
            COMPOSE_CMD="docker compose"
            COMPOSE_VER="$(docker compose version --short 2>/dev/null || echo 'desconocida')"
        else
            error "Docker Compose no está disponible. Instálalo desde https://docs.docker.com/compose/install/"
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
    install_pkg python3 python3-pip python3-venv
    ok "Python instalado"
}

check_python() {
    if ! check_cmd python3; then
        if ! check_cmd python; then
            warn "Python 3 no está instalado"
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
        install_pkg python3-pip
    fi
    ok "pip disponible"
}

# ==============================================================================
# Node.js + npm
# ==============================================================================

install_node() {
    info "Instalando Node.js 20 LTS..."
    
    if [ "$DISTRO" = "ubuntu" ] || [ "$DISTRO" = "debian" ]; then
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt-get install -y -qq nodejs
    else
        warn "Instalación automática de Node.js no soportada en $DISTRO"
        warn "Instálalo manualmente desde https://nodejs.org/ (requiere Node 20+)"
        return 1
    fi
    ok "Node.js instalado"
}

check_node() {
    if ! check_cmd node; then
        warn "Node.js no está instalado"
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
    install_pkg postgresql postgresql-contrib postgresql-client
    start_service postgresql
    ok "PostgreSQL instalado"
}

check_postgres_local() {
    if ! check_cmd psql; then
        warn "Cliente psql no disponible"
        install_postgres || {
            warn "PostgreSQL no instalado. Se usará el contenedor Docker 'db'."
            return
        }
    else
        ok "Cliente psql $(psql --version | awk '{print $3}') disponible"
    fi
    if ! check_cmd pg_isready; then
        warn "pg_isready no disponible, puede que PostgreSQL no esté corriendo"
        start_service postgresql
    fi
    if pg_isready -q; then
        ok "PostgreSQL server está corriendo localmente"
    else
        warn "PostgreSQL server local no disponible. Se usará el contenedor Docker 'db'."
    fi
}

# ==============================================================================
# Redis local
# ==============================================================================

install_redis() {
    info "Instalando Redis..."
    install_pkg redis-server
    start_service redis-server
    ok "Redis instalado"
}

check_redis_local() {
    if ! check_cmd redis-cli; then
        warn "redis-cli no disponible"
        install_redis || {
            warn "Redis no instalado. Se usará el contenedor Docker 'redis'."
            return
        }
    else
        ok "redis-cli disponible"
    fi
    if ! redis-cli ping >/dev/null 2>&1; then
        warn "Redis no está corriendo localmente"
        start_service redis-server
        sleep 1
        redis-cli ping >/dev/null 2>&1 && ok "Redis corriendo" || warn "Redis sigue sin responder. Se usará contenedor Docker."
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
        warn "No se encontró ni .env ni .env.example"
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
            warn "Carpeta frontend/ssl/ existe pero no contiene certificados válidos (.crt/.key)"
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
    info "=== Transcendence Team - Preparación de entorno ==="
    echo ""

    detect_distro
    info "Distribución: $PRETTY_NAME ($DISTRO)"
    echo ""

    check_make
    check_git
    check_docker
    check_docker_compose
    check_python
    check_node
    check_env
    check_postgres_local
    check_redis_local
    check_angular_cli
    check_ssl_certs

    echo ""
    ok "=== Verificación completada ==="
    info "Para ejecutar el proyecto:"
    info "  - Desarrollo : make dev"
    info "  - Producción : make prod"
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        info "  - Generar .env: make env MODE=dev  (o MODE=prod)"
    fi
}

main
