#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$LOG_PREFIX = "[SETUP]"

function Log-Info {
    param([string]$Message)
    Write-Host "$LOG_PREFIX [INFO]  $Message" -ForegroundColor Cyan
}

function Log-Ok {
    param([string]$Message)
    Write-Host "$LOG_PREFIX [OK]    $Message" -ForegroundColor Green
}

function Log-Warn {
    param([string]$Message)
    Write-Host "$LOG_PREFIX [WARN]  $Message" -ForegroundColor Yellow
}

function Log-Error {
    param([string]$Message)
    Write-Host "$LOG_PREFIX [ERROR] $Message" -ForegroundColor Red
}

# ==============================================================================
# Utilidades
# ==============================================================================

function Test-Command {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Install-Package {
    param([string[]]$Packages)
    Log-Info "Instalando paquetes via winget: $($Packages -join ', ')"
    foreach ($pkg in $Packages) {
        $pkgId = $pkg.Split('|')[0]
        $wingetArgs = @(
            "install", "--id", $pkgId
            "--accept-source-agreements", "--accept-package-agreements"
            "--silent"
        )
        winget install @wingetArgs 2>$null
        if ($LASTEXITCODE -ne 0) {
            Log-Warn "winget no pudo instalar $pkgId, intentando con la instalacion..."
            Start-Process winget -ArgumentList @("install", "--id", $pkgId, "--silent") -Wait
        }
    }
}

# ==============================================================================
# Docker Desktop (Windows)
# ==============================================================================

function Install-DockerDesktop {
    Log-Info "Instalando Docker Desktop para Windows..."
    Log-Info "Descargando instalador desde https://desktop.docker.com/"
    $installer = "$env:TEMP\DockerDesktopInstaller.exe"
    try {
        Invoke-WebRequest -Uri "https://desktop.docker.com/win/stable/Docker%20Desktop%20Installer.exe" -OutFile $installer -UseBasicParsing 2>$null
    } catch {
        Log-Warn "No se pudo descargar Docker Desktop automaticamente"
        return $false
    }
    Start-Process -FilePath $installer -ArgumentList "/quiet", "install" -Wait
    Remove-Item $installer -ErrorAction SilentlyContinue
    Log-Ok "Docker Desktop instalado. Reinicia la sesion para complete la configuracion"
    return $true
}

function Check-Docker {
    if (-not (Test-Command docker)) {
        Log-Warn "Docker CLI no esta instalado"
        Log-Info "En Windows se usa Docker Desktop como opcion estandar"
        Install-DockerDesktop
        if (-not (Test-Command docker)) {
            Log-Error "Docker Desktop no se pudo instalar automaticamente"
            Log-Info "Descargalo desde: https://www.docker.com/products/docker-desktop/"
            exit 1
        }
    }

    try {
        docker info 2>$null | Out-Null
    } catch {
        Log-Warn "Docker Desktop no esta corriendo. Intentando iniciar..."
        Start-Service com.docker.service -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 5
        try {
            docker info 2>$null | Out-Null
        } catch {
            Log-Error "Docker Desktop esta instalado pero no se pudo iniciar. Iniciacalo manualmente."
            exit 1
        }
    }

    $dockerVer = (docker --version 2>$null) -replace 'Docker version ', '' -replace ',.*', ''
    $serverVer = (docker info --format "{{.ServerVersion}}" 2>$null)
    if (-not $serverVer) { $serverVer = "desconocida" }
    Log-Ok "Docker $dockerVer (server: $serverVer)"
}

# ==============================================================================
# Docker Compose
# ==============================================================================

function Check-DockerCompose {
    $composeCmd = $null
    $composeVer = $null

    if (Test-Command docker-compose) {
        $composeCmd = "docker-compose"
        $composeVer = (docker-compose --version 2>$null) -replace '.*(\d+\.\d+\.\d+).*', '$1'
    } elseif (Test-Command docker) {
        try {
            $composeVer = (docker compose version --short 2>$null) -replace 'v', ''
            if ($composeVer) {
                $composeCmd = "docker compose"
            }
        } catch { }
    }

    if (-not $composeCmd) {
        Log-Warn "Docker Compose plugin no detectado"
        Log-Info "Docker Compose viene incluido con Docker Desktop para Windows"
        Log-Info "Asegurate de que Docker Desktop esta en ejecucion"
        if (-not (Test-Command docker)) {
            Log-Error "Docker Compose no esta disponible. Instala Docker Desktop desde https://www.docker.com/products/docker-desktop/"
            exit 1
        }
        try {
            $composeVer = (docker compose version --short 2>$null) -replace 'v', ''
            $composeCmd = "docker compose"
        } catch {
            Log-Error "Docker Compose no esta disponible. Instalo desde https://docs.docker.com/compose/install/"
            exit 1
        }
    }

    Log-Ok "Docker Compose $composeVer (usando: $composeCmd)"
}

# ==============================================================================
# Python + pip
# ==============================================================================

function Install-Python {
    Log-Info "Instalando Python 3 y pip..."
    Install-Package @("Python.Python.3.12", "Python.Python.3.11", "Python.Python.3.10")
    Log-Ok "Python instalado"
}

function Check-Python {
    if (-not (Test-Command python) -and -not (Test-Command python3)) {
        Log-Warn "Python 3 no esta instalado"
        Install-Python
        if (-not (Test-Command python) -and -not (Test-Command python3)) {
            Log-Error "Instala Python 3.10+ manualmente desde https://www.python.org/downloads/"
            exit 1
        }
    }

    $pythonCmd = if (Test-Command python3) { "python3" } else { "python" }
    $pythonVer = & $pythonCmd --version 2>&1 | Out-String
    $pythonVer = $pythonVer.Trim() -replace 'Python ', ''

    $major = & $pythonCmd -c "import sys; print(sys.version_info.major)" 2>$null
    $minor = & $pythonCmd -c "import sys; print(sys.version_info.minor)" 2>$null

    if ([int]$major -lt 3 -or ([int]$major -eq 3 -and [int]$minor -lt 10)) {
        Log-Warn "Python $pythonVer detectado. Se recomienda Python 3.10+"
    } else {
        Log-Ok "Python $pythonVer"
    }

    if (-not (Test-Command pip) -and -not (Test-Command pip3)) {
        Log-Warn "pip no encontrado, instalando..."
        Install-Package @("Python.Python.3.12")
    }
    Log-Ok "pip disponible"
}

# ==============================================================================
# Node.js + npm
# ==============================================================================

function Install-Node {
    Log-Info "Instalando Node.js 20 LTS..."
    Install-Package @("OpenJS.NodeJS.Current")
    Log-Ok "Node.js instalado"
}

function Check-Node {
    if (-not (Test-Command node)) {
        Log-Warn "Node.js no esta instalado"
        Install-Node
        if (-not (Test-Command node)) {
            Log-Error "Instala Node.js 20+ manualmente desde https://nodejs.org/"
            exit 1
        }
    }

    $nodeVer = node --version
    $nodeMajor = [int](node -e "console.log(process.versions.node.split('.')[0])" 2>$null)
    $npmVer = npm --version 2>$null

    if ($nodeMajor -lt 20) {
        Log-Warn "Node $nodeVer detectado. Se requiere Node.js 20+. Actualizando..."
        Install-Node
        $nodeVer = node --version
        $nodeMajor = [int](node -e "console.log(process.versions.node.split('.')[0])" 2>$null)
        if ($nodeMajor -lt 20) {
            Log-Warn "Node.js sigue siendo antiguo. Considera actualizar manualmente."
        }
    } else {
        Log-Ok "Node.js $nodeVer"
    }

    if (-not (Test-Command npm)) {
        Log-Warn "npm no encontrado junto a Node.js"
        Install-Node
    }
    Log-Ok "npm $npmVer"
}

# ==============================================================================
# PostgreSQL local (via Docker en Windows)
# ==============================================================================

function Check-PostgresLocal {
    if (-not (Test-Command psql)) {
        Log-Warn "psql no esta disponible en Windows"
        Log-Info "Usara el contenedor Docker 'db' para PostgreSQL"
        return
    }

    Log-Ok "Cliente psql disponible"
    try {
        $ready = pg_isready 2>$null
        if ($LASTEXITCODE -eq 0) {
            Log-Ok "PostgreSQL server esta corriendo localmente"
        } else {
            Log-Warn "PostgreSQL server local no disponible. Usara el contenedor Docker 'db'."
        }
    } catch {
        Log-Warn "pg_isready no disponible. Usara el contenedor Docker 'db'."
    }
}

# ==============================================================================
# Redis local (via Docker en Windows)
# ==============================================================================

function Check-RedisLocal {
    if (-not (Test-Command redis-cli)) {
        Log-Warn "redis-cli no disponible en Windows"
        Log-Info "Usara el contenedor Docker 'redis' para Redis"
        return
    }

    Log-Ok "redis-cli disponible"
    try {
        $ping = redis-cli ping 2>$null
        if ($ping -match "PONG") {
            Log-Ok "Redis corriendo localmente"
        } else {
            Log-Warn "Redis no esta corriendo localmente. Usara el contenedor Docker 'redis'."
        }
    } catch {
        Log-Warn "Redis no se pudo conectar localmente. Usara el contenedor Docker 'redis'."
    }
}

# ==============================================================================
# Angular CLI (opcional)
# ==============================================================================

function Install-AngularCli {
    Log-Info "Instalando Angular CLI globalmente..."
    npm install -g @angular/cli 2>$null
    if ($LASTEXITCODE -ne 0) {
        Log-Warn "No se pudo instalar Angular CLI globalmente"
        return $false
    }
    Log-Ok "Angular CLI instalado"
    return $true
}

function Check-AngularCli {
    if (-not (Test-Command ng)) {
        Log-Warn "Angular CLI no instalado"
        Install-AngularCli
    } else {
        $ngVer = (ng version 2>$null) | Select-String "Angular CLI" | ForEach-Object { ($_ -replace '.*Angular CLI ', '') -replace '\..*', '' }
        if ($ngVer) {
            Log-Ok "Angular CLI $ngVer disponible"
        } else {
            Log-Ok "Angular CLI disponible"
        }
    }
}

# ==============================================================================
# Variables de entorno
# ==============================================================================

function Check-Env {
    $envFile = Join-Path $SCRIPT_DIR ".env"
    $envExample = Join-Path $SCRIPT_DIR ".env.example"

    if (Test-Path $envFile) {
        Log-Ok ".env existe"
        $content = Get-Content $envFile -Raw -ErrorAction SilentlyContinue
        if ($content -match "^SUPER_ADMIN_PASSWORD=") {
            Log-Ok "SUPER_ADMIN_PASSWORD definida en .env"
        } else {
            Log-Warn "SUPER_ADMIN_PASSWORD no definida en .env. Ejecuta 'make env' para generarla."
        }
    } elseif (Test-Path $envExample) {
        Log-Warn ".env no existe, pero hay .env.example"
        Log-Info "  -> cp .env.example .env"
        Log-Info "  -> make env MODE=dev (o MODE=prod)"
    } else {
        Log-Warn "No se encontro ni .env ni .env.example"
        Log-Info "  -> Ejecuta 'make env' para generar .env interactivamente"
    }
}

# ==============================================================================
# SSL
# ==============================================================================

function Check-SSLCerts {
    $sslDir = Join-Path $SCRIPT_DIR "frontend" "ssl"
    if (Test-Path $sslDir) {
        $crtFiles = Get-ChildItem -Path $sslDir -Filter "*.crt" -ErrorAction SilentlyContinue
        $keyFiles = Get-ChildItem -Path $sslDir -Filter "*.key" -ErrorAction SilentlyContinue
        if ($crtFiles -and $keyFiles) {
            Log-Ok "Certificados SSL locales encontrados en frontend/ssl/"
        } else {
            Log-Warn "Carpeta frontend/ssl/ existe pero no contiene certificados validos (.crt/.key)"
        }
    } else {
        Log-Warn "Carpeta frontend/ssl/ no existe"
    }
}

# ==============================================================================
# Git / Make
# ==============================================================================

function Check-Git {
    if (Test-Command git) {
        $gitVer = (git --version 2>$null) -replace 'git version ', ''
        Log-Ok "Git $gitVer disponible"
    } else {
        Log-Warn "Git no detectado. Instalando..."
        Install-Package @("Git.Git")
    }
}

function Check-Make {
    if (Test-Command make) {
        Log-Ok "Make disponible"
    } else {
        Log-Warn "Make no detectado"
        Log-Info "Make esta disponible via Git Bash (viene con Git for Windows)"
        Log-Info "Si usas PowerShell puro, considera instalar MSYS2 para tener make"
        Log-Info "Descarga Git for Windows: https://git-scm.com/download/win"
    }
}

# ==============================================================================
# MAIN
# ==============================================================================

function Main {
    Log-Info "=== Transcendence Team - Preparacion de entorno (Windows) ==="
    Write-Host ""

    $osName = ([System.Runtime.InteropServices.RuntimeInformation]::OSDescription)
    if ($osName -match "Windows") {
        $winVer = [System.Environment]::OSVersion.Version.ToString()
        Log-Info "Platform: Windows $winVer"
    } else {
        Log-Warn "Este script esta disenado para Windows"
        Log-Warn "Se detecto: $osName"
    }
    Write-Host ""

    if (-not (Test-Command winget)) {
        Log-Error "winget no esta disponible. Es necesario para Windows 10/11."
        Log-Info "Habilita winget desde Microsoft Store o actualiza Windows."
        exit 1
    }

    Check-Make
    Check-Git
    Check-Docker
    Check-DockerCompose
    Check-Python
    Check-Node
    Check-Env
    Check-PostgresLocal
    Check-RedisLocal
    Check-AngularCli
    Check-SSLCerts

    Write-Host ""
    Log-Ok "=== Verificacion completada ==="
    Log-Info "Para ejecutar el proyecto:"
    Log-Info "  - Desarrollo : make dev"
    Log-Info "  - Produccion : make prod"
    $envFile = Join-Path $SCRIPT_DIR ".env"
    if (-not (Test-Path $envFile)) {
        Log-Info "  - Generar .env: make env MODE=dev  (o MODE=prod)"
    }
}

Main