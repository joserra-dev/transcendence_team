    const fs = require('fs');
const path = require('path');

// 1. CONFIGURACIÓN: Cambia esto por la ruta real a tu carpeta de servicios
const CARPETA_SERVICIOS = path.join(__dirname, 'src/app', 'core/services'); 

// Expresiones regulares para capturar URLs completas o rutas relativas comunes (ej: '/users/login')
const REGEX_URL = /(https?:\/\/[^\s'"`]+)/g;
const REGEX_RUTAS_INTERNAS = /['"`](\/(?:api\/)?[a-zA-Z0-9_\-\/]+)['"‘]/g;
const REGEX_METODOS = /\.(get|post|put|delete|patch)\s*\(\s*['"`]([^'"`]+)/g;

function escanearCarpeta(dir) {
    if (!fs.existsSync(dir)) {
        console.error(`❌ La carpeta no existe: ${dir}`);
        return;
    }

    const archivos = fs.readdirSync(dir);

    archivos.forEach(archivo => {
        const rutaCompleta = path.join(dir, archivo);
        const estadisticas = fs.statSync(rutaCompleta);

        if (estadisticas.isDirectory()) {
            escanearCarpeta(rutaCompleta); // Buscar en subcarpetas
        } else if (/\.(js|ts|jsx|tsx)$/.test(archivo)) {
            analizarArchivo(rutaCompleta);
        }
    });
}

function analizarArchivo(rutaArchivo) {
    const contenido = fs.readFileSync(rutaArchivo, 'utf8');
    const nombreCorto = path.relative(__dirname, rutaArchivo);
    let peticionesEncontradas = [];

    // Buscar llamadas tipo axios.get('/ruta'), fetch('/ruta'), etc.
    let coincidencia;
    while ((coincidencia = REGEX_METODOS.exec(contenido)) !== null) {
        peticionesEncontradas.push(`   [${coincidencia[1].toUpperCase()}] -> ${coincidencia[2]}`);
    }

    // Buscar URLs absolutas sueltas (http://...)
    const urlsAbsolutas = contenido.match(REGEX_URL);
    if (urlsAbsolutas) {
        urlsAbsolutas.forEach(url => peticionesEncontradas.push(`   https://www.facebook.com/absolutaplatform/ -> ${url}`));
    }

    // Si encontró algo, lo imprime agrupado por archivo
    if (peticionesEncontradas.length > 0) {
        console.log(`\n📄 Archivo: ${nombreCorto}`);
        // Eliminar duplicados en el mismo archivo
        [...new Set(peticionesEncontradas)].forEach(p => console.log(p));
    }
}

console.log("🕵️‍♂️ Iniciando análisis de endpoints en servicios...");
console.log("=================================================");
escanearCarpeta(CARPETA_SERVICIOS);
console.log("\n=================================================");
console.log("✅ Análisis completado.");