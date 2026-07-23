
### Resumen de cambios realizados (26-06-10):
  
  1. Modelo de Camping (Backend):
      • Modifiqué el método  to_dict  de la clase  Parking  en parking.py para que determine dinámicamente si  
      cada parcela está libre ( estado = "0" ) u ocupada ( estado = "1" ) en base a un rango de fechas.            
  2. Rutas del Buscador (Backend):
      • Actualicé la función  search_parkings  en parking_routes.py para capturar los parámetros de consulta  id , fechaDesde  y  fechaHasta , y pasarlos a la serialización del modelo.
  3. Servicios de Búsqueda (Frontend):
      • Modifiqué el método  searchParkings  en el servicio parking.ts para enviar correctamente todos los     
      filtros activos (incluyendo las fechas de reserva y el municipio/provincia) al backend local.
  4. Redirección de Reservas en Local (Frontend):
      • Cambié la URL base del servicio booking.ts de la API externa (Render) a la API local (http://localhost:5000/api ) para que todas las reservas se procesen y guarden localmente.
  5. API de Reservas Completa (Backend):
      • Re-escribí por completo booking_routes.py para dar soporte local a los siguientes endpoints que el frontend  
      consume:
          •  POST /api/reserva : Crea reservas nuevas con validación de solapamiento de fechas (si la parcela ya   
          está reservada en esas fechas, devuelve error).
          •  GET /api/reserva/<id> : Obtiene detalles de una reserva formateada.
          •  GET /api/historico/listado : Retorna el historial de reservas del usuario.
          •  PUT /api/reserva/cancelar : Cancela una reserva (cambia su estado a  "0" ).
          •  PUT /api/reserva/puntuar : Permite puntuar el camping una vez reservado.
          •  POST /api/reserva/qr : Retorna un código QR representativo en formato base64.
   
    6. COMENTADO en parking-details.ts linea 115-118

        # ¿Cuál era el error exacto?
  
            1. Falta de campo en Base de Datos: El backend no tenía la columna  iban  en su modelo de perfil ni en la tabla  
            de PostgreSQL para almacenar la cuenta bancaria del usuario.
            2. EndPoint Inexistente: El frontend enviaba las actualizaciones de perfil (nombre, apellidos, DNI, fecha de     
            nacimiento e IBAN) a  PUT /api/users/update , pero ese endpoint no existía en el Flask local.
            3. Serialización Incompleta: Los endpoints  /me  y  /perfil  en el backend no devolvían los datos del perfil     
            (solo devolvían  id  e  email ), por lo que el formulario de perfil del cliente siempre se inicializaba vacío,   
            forzando la validación del IBAN a fallar cada vez.
            ──────
    # Solución aplicada:
            
            1. Ampliación del Modelo (Backend):
                • Agregué la columna  iban  al modelo  Profiles  en users.py.
            2. Actualización Automática de Base de Datos:
                • En app.py, agregué una instrucción SQL  ALTER TABLE  dinámica que crea la columna  iban  si ya     
                existe la base de datos de PostgreSQL persistida de antes.
            3. Implementación de Endpoints y Serialización:
                • Creé un serializador completo en users_routes.py para mapear todos los campos que el frontend espera en  /me
                y  /perfil .
                • Implementé el endpoint  PUT /api/users/update  para guardar los cambios del perfil (nombre, apellidos,     
                fecha de nacimiento, IBAN y contraseña).
            4. Activación de Validación de Pago (Frontend):
                • Descomenté la comprobación en parking-detail.ts (líneas 115-118). Ahora, si un usuario intenta reservar pero 
                no tiene un IBAN configurado en su cuenta, se le redirige automáticamente a su página de perfil para que lo  
                introduzca de forma segura, en lugar de lanzar un error silencioso de API.

    7. 2. ### Resumen de cambios:                                                                                                                                               
                                                                                                                                                                        
  1. Ampliación en Base de Datos (Backend):                                                                                                                             
      • Agregué las columnas  metodo_pago  y  tarjeta  a la tabla  public.profiles  en users.py.                                                                  
      • Añadí sentencias SQL  ALTER TABLE  automáticas en app.py para crear estas columnas dinámicamente si ya existiera la base de datos de PostgreSQL.        
  2. Endpoints de Perfil (Backend):                                                                                                                                     
      • Modifiqué el serializador de usuarios y las rutas  /me ,  /perfil  y  /update  en users_routes.py para soportar el guardado y recuperación de  metodoPago  y     
      tarjeta .                                                                                                                                                         
  3. Modelo de Usuario (Frontend):                                                                                                                                      
      • Declaré  metodoPago  y  tarjeta  en la interfaz user.ts.                                                                                                 
  4. Formulario de Perfil (Frontend):                                                                                                                                   
      • En profile.ts, añadí un validador condicional ( paymentMethodValidator ) que:                                                                               
          • Si selecciona IBAN (Cuenta Bancaria): Exige un IBAN y valida que comience por  ES  y tenga 22 dígitos.                                                      
          • Si selecciona Tarjeta de Crédito: Exige un número de tarjeta y valida que contenga exactamente 16 dígitos numéricos.                                        
          • Si selecciona Efectivo: Permite guardar sin ningún campo adicional.                                                                                         
      • En profile.html, añadí un control desplegable ( select ) para el método de pago y las entradas condicionales que se muestran dinámicamente según la opción    
      elegida.                                                                                                                                                          
      • Modifiqué el guardado de perfil exitoso para actualizar la sesión en  localStorage  inmediatamente para evitar problemas de caché.                              
  5. Flujo de Reserva (Frontend):                                                                                                                                       
      • En parking-detail.ts, restauré y amplié el bloqueo de reserva: ahora comprueba si el usuario tiene configurado un método de pago válido completo (IBAN válido, tarjeta válida, o efectivo). Si no tiene ninguno, lo redirige al perfil para configurarlo antes de permitirle reservar.  

      ### Resumen de adiciones para Pago en Efectivo:
  
  1. Mensaje informativo en el Perfil (Frontend):
      • Agregué un cuadro informativo dinámico en profile.html que aparece al seleccionar "Efectivo" indicando que el abono se realizará de forma presencial          
      directamente en el camping al llegar.
  2. Visualización en el modal de reservas (Frontend):
      • En parking-detail.ts, implementé el helper  getPaymentMethodLabel()  para formatear de forma segura el método de pago activo del usuario (enmascarando las
        tarjetas
      o cuentas bancarias y mostrando la aclaración para efectivo).
      • En parking-detail.html, modifiqué el cuadro resumen del modal de confirmación para que muestre exactamente el método de pago seleccionado por el usuario (ej.
    "Pago en Efectivo (Se abonará al llegar)").


      

    7. botones de navegacion en paginas <- ->.

        7. 1. boton de salir/guardar en la pagina "mis datos"

    8. control de reservas get/push o trigger



## Otros problemas encontrados

### 1. **`matchPasswords` no es condicional** (el más importante)
El validador `matchPasswords` en [custom-validators.ts](file:///home/jrc/Escritorio/transcendence_team/frontend/camper/src/app/shared/validators/custom-validators/custom-validators.ts#L47-L53) compara las contraseñas **siempre**, incluso cuando ambas están vacías. Esto hace que el formulario sea **inválido** en el estado inicial (cargando el perfil), porque `'' === ''` sí funciona, pero cuando el usuario solo rellena el password sin el confirm, bloquea el guardado innecesariamente. El problema real: **si el usuario no quiere cambiar la contraseña y deja ambos campos vacíos, debería ser válido**.

### 2. **`paymentMethodValidator` tiene un bug con `select [disabled]`** 
En el HTML, el `<select>` usa `[disabled]="!isEditing"` con binding dinámico. En Angular Reactive Forms, deshabilitar un control del template así **no funciona correctamente** — puede que el valor del `metodoPago` se pierda o no se envíe al backend.

### 3. **Error de mensaje incorrecto en fecha** (línea 59-61 del HTML)
Cuando `fecNacimientoPersona` es inválido, siempre muestra `PROFILE.ERROR.UNDER_AGE`, pero el campo también tiene `Validators.required`, por lo que si está vacío debería mostrar "requerido", no "menor de edad".

### 4. **`CustomValidators` tiene decorador `@Component` encima** 
El archivo [custom-validators.ts](file:///home/jrc/Escritorio/transcendence_team/frontend/camper/src/app/shared/validators/custom-validators/custom-validators.ts#L4-L9) tiene un decorador `@Component` que no tiene ningún sentido en una clase de utilidades. Aunque no rompe el funcionamiento, es código incorrecto que puede causar problemas con el compilador de Angular.


Los cambios serían:

1. **`custom-validators.ts`** → Quitar `@Component`, hacer `matchPasswords` condicional (solo valida si alguna contraseña tiene valor)
2. **`profile.ts`** → Usar `.disable()` / `.enable()` para el select en lugar de `[disabled]` en el template
3. **`profile.html`** → Distinguir mensajes de error en el campo fecha (requerido vs menor de edad)



### 26/06/11 analisis_login_sesion.md

## Estado del Login y Sesiones

### ✅ Lo que funciona bien
- Login/logout básico con `localStorage` (token + user)
- El interceptor añade el `Bearer token` a las peticiones
- Al intentar reservar sin sesión, redirige al login con `returnUrl`

### 🚨 Problemas encontrados (por prioridad) 

**1. No hay Route Guards (crítico)**  
Las rutas `/client/history`, `/client/profile`, `/admin/*` son accesibles directamente desde la URL sin estar logueado. No existe ningún `canActivate` en `client.routes.ts` ni en `admin.routes.ts`.

**2. El interceptor no maneja el 401 (crítico para inactividad)**  
Si el token expira (el backend usa flask-jwt-extended con 15 min por defecto), el interceptor simplemente deja pasar el error. El usuario queda en estado zombie: la UI muestra que está logueado pero todas las peticiones fallan. **Este es el problema principal con la inactividad.**

**3. El login devuelve un usuario incompleto**  
El endpoint `/api/users/login` solo devuelve `id` y `email`, pero el frontend necesita `admin`, `metodoPago`, `ibanPersona`, etc. Hay que usar `_user_to_frontend_dict()` también en el login.

**4. `isLoggedIn()` no valida expiración**  
Solo comprueba si existe el string en `localStorage`, no si el JWT ha expirado.



🆕 Archivos nuevos
Archivo	                    Qué hace
core/guards/auth.guard.ts	Si no hay sesión → redirige a /auth/login-client con returnUrl
core/guards/admin.guard.ts	Si no es admin → redirige al home (o login si no hay sesión)


✏️ Archivos modificados
client.routes.ts — Las 3 rutas (history, profile, booking/:id) ahora tienen canActivate: [authGuard].

admin.routes.ts — Las 3 rutas (dashboard, parking/new, parking/:id) ahora tienen canActivate: [adminGuard].

auth-interceptor.ts — Ahora captura errores HTTP 401. Si el backend responde con 401 (token expirado por inactividad), llama automáticamente a authService.logout(), que limpia el localStorage y redirige al login.

auth.ts → isLoggedIn() — Ahora decodifica el payload del JWT con atob() (sin librerías extra) y comprueba el campo exp. Si el token ha expirado, lo elimina del localStorage y devuelve false inmediatamente.

users_routes.py → /login — Ahora devuelve el usuario completo (nombre, apellidos, admin, iban, metodoPago, etc.) usando _user_to_frontend_dict(), la misma función que ya se usaba en /me.



### 5. 26/06/12 he instalado node.js


# Instalar Node.js (incluye npm) vía nvm (más limpio)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
# Reabrir terminal, luego:
nvm install --lts
# Luego en la carpeta del proyecto:
cd /home/jrc/Escritorio/transcendence_team/frontend/camper
npm install

"NO ME GUSTA COMO FUNCIONA EL LOGIN DESPUES DE HACER VARIOS RETOQUES"

### 6. 26/06/14 deberiamos lanzar un spam en caso de que el usuario tenga una reserva activa en las mismas fechas

He añadido la comprobación para que no se puedan reservar varias plazas solapando las fechas y, si ocurre, mostrará una alerta (un "spam" de advertencia) en la pantalla.

He realizado dos modificaciones:

Backend (booking_routes.py): He añadido una validación adicional durante la creación de la reserva (POST /api/reserva). Ahora, además de comprobar si la plaza concreta está ocupada, se busca en la base de datos si el mismo usuario (id_user) ya tiene una reserva con el estado confirmado ("1") en esas fechas. Si es así, devolverá el error: "Ya tienes una reserva para ti en estas fechas. No puedes reservar más de una plaza a la vez." con un código HTTP 400.
Frontend (parking-detail.ts): He modificado cómo se maneja el error al confirmar una reserva. Ahora el frontend comprobará si el servidor devolvió un mensaje de texto con el error, lo asignará a la variable de error de la vista y lanzará un agresivo popup de alerta usando alert("⚠️ ATENCIÓN: " + errorMsg) en el navegador, asegurando que el usuario lo vea de inmediato.


### 7. guardamos sesion en localsession en vez de localstorage


### 8. 26/06/19 revision contra subject
He revisado el subject y aplicado mejoras críticas para cumplir mejor con transcendence_en.subject.pdf.

Cambios principales:

README.md reescrito en inglés con las secciones exigidas: equipo, gestión, stack, schema, features, módulos, contribuciones, IA y legal.
Añadidas páginas legales accesibles:
/legal/privacy
/legal/terms
Footer actualizado con enlaces a privacidad y términos.
Añadido .env.example.
.env eliminado del índice de Git para evitar subir secretos.
Añadidos endpoints admin que faltaban:
GET/POST/PUT /api/admin/parking
GET/PUT/DELETE /api/admin/parking/:id/space/:id
GET /api/admin/parking/space/:id
Añadida API pública con API key y rate limit:
GET/POST/GET /api/public/parkings...
PUT /api/public/spaces/:id/status
DELETE /api/public/spaces/:id
Añadido health check:
GET /api/status
Corregido solapamiento de reservas para detectar intervalos parciales.
Añadido email de confirmación de reserva.
Perfil de usuario ampliado con avatar URL.
Corregidos tests existentes.
Docker backend corregido para lanzar Flask correctamente.
Validaciones:

git diff --check: correcto.

compileall backend: correcto.
Angular build: correcto.
Angular tests: compilan, pero no se ejecutan porque falta ChromeHeadless en el entorno.

Pendiente crítico:

Despliegue real debe hacerse con HTTPS válido. Local puede seguir en HTTP, pero para evaluación conviene desplegar detrás de dominio HTTPS o configurar Caddy/Nginx con certificados.

otros cambios:

Backend POST /api/booking ahora permite reservas en fechas coincidentes si la matrícula es diferente.
Bloquea duplicados solo cuando la misma matrícula ya tiene una reserva activa en esas fechas.
Frontend permite seleccionar plazas marcadas como ocupadas.
El modal muestra aviso: puedes continuar si la matrícula es diferente.

Añadidos mensajes i18n en ES/EN/EU.

Validado:

compileall backend: correcto.

Angular build: correcto.
git diff --check: correcto.

Añadida la matrícula visible en reservas.

Cambios:

Backend devuelve licensePlate en detalle de reserva y en historial.
Historial muestra la matrícula en cada tarjeta.
Detalle de reserva muestra la matrícula en información general.
Modal “Ver matrícula” usa directamente la matrícula ya cargada.
Traducciones añadidas en ES/EN/EU.
Validado:

Backend compile: correcto.

Angular build: correcto.
git diff --check: correcto.

### 26/06/19 revision de ultimas modificaciones
- las traducciones no son limpias
- las fechas de las reservas no me modifica automaticamente al dia siguiente o dejarmelo vacio

### 26/06/22 revision facturacion y legal / terms
El fallo venía de que LegalPage reutilizaba el mismo componente y solo leía el parámetro con snapshot; al cambiar entre /legal/privacy y /legal/terms no volvía a ejecutarse ngOnInit.

Cambios:

frontend/camper/src/app/features/legal/legal-page.ts:18 ahora escucha route.paramMap para actualizar pageType al cambiar de página.
frontend/camper/src/app/features/legal/legal-page.ts:22 también devuelve el scroll arriba al cambiar.
frontend/camper/src/app/features/legal/legal-page.ts:26 libera la suscripción al destruir el componente.


También corregí el cálculo que cobraba un día de más:

Backend: backend/area_backend/routes/booking_routes.py:27, :119, :192
Frontend: frontend/camper/src/app/features/public/parking-detail/parking-detail.ts:125

### 26/06/23 correccion solapamiento reservas

backend/area_backend/models/parking.py:66-71 la comprobación de disponibilidad de plazas usa < y > en lugar de <= y >=.

Esto significa que:

Si tienes una reserva que termina el día X, puedes reservar la misma plaza para el día X (u otro período posterior).
Si tienes una reserva que empieza el día X, puedes reservar la misma plaza para el día X (u otro período anterior).
Los solapamientos reales siguen bloqueados.
Consistente con la lógica de la matrícula (salida 12:00, entrada 15:00).

### 26/06/25 modificacion templates (control de errores)
Los cambios son:

Backend (backend/area_backend/routes/parking_routes.py):

Agregué control de error 404 cuando se busca un parking por ID y no existe
Frontend (frontend/camper/src/app/features/public/parking-detail/):

parking-detail.ts: Agregué manejo de error 404 en la suscripción del servicio
parking-detail.html: Reordené el template para mostrar error antes del loading
i18n/es.json, i18n/en.json, i18n/eu.json: Agregué clave NOT_FOUND con los mensajes de error

### 26/06/28 correccion de uso de fechas

## Revisión de código relacionado con fechas

Encontré **25 errores y problemas** en el manejo de fechas en backend y frontend:

---

### Backend

| # | Archivo:línea | Tipo | Descripción |
|---|---------------|------|-------------|
| 1 | `booking_routes.py:46` | **Bug crítico** | Devuelve `"starDate"` en vez de `"startDate"` (typo). El frontend espera `startDate` en `BookingHistoryResponse` y `AdminBooking`; el valor será `undefined` y las fechas no se mostrarán. **Arreglar:** cambiar `"starDate"` por `"startDate"`. |
| 2 | `booking_routes.py:28` y `:185` | **Inconsistencia** | Calcula días con `max((end - start).days, 0)`. Una reserva de un solo día (misma fecha entrada y salida) da 0 días = precio 0. **Arreglar:** usar `+ 1` como en admin, o rechazar salida = entrada (ya lo hace en línea 280). |
| 3 | `admin_routes.py:107` | **Inconsistencia** | Calcula días con `(end - start).days + 1`, contando inclusivo. El endpoint de usuario usa `max(..., 0)` sin `+1`. Los precios difieren entre panel admin y vista de usuario. **Arreglar:** unificar la lógica. |
| 4 | `public_api_routes.py:115-116` | **Bug / Falta de robustez** | `datetime.strptime(to_date, '%Y-%m-%d')` sin `try/except`. Si el JSON trae un formato inválido, lanza 500 en vez de 400. **Arreglar:** envolver en `try/except ValueError`. |
| 5 | `booking_routes.py:275-278` | **Bug potencial** | `datetime.strptime(start_date, "%Y-%m-%d")` falla si el input viene como ISO completo (`2026-07-01T00:00:00`) desde un `datetime-local`. **Arreglar:** usar `start_date[:10]` antes de parsear. |
| 6 | `public_api_routes.py:113-118` | **Inconsistencia lógica** | Usa `<=` y `>=` para overlap, mientras `booking_routes.py:285-286` usa `<` y `>`. La API pública marca ocupado un espacio que en la web se podría reservar. **Arreglar:** alinear con `<`/`>` como en el resto. |
| 7 | `parking_routes.py:84-85` | **Validación nula** | Pasa `from_date` y `to_date` a `to_dict()` sin validar formato. Si llega `fechaDesde=foo`, el modelo hace `print` pero sigue devolviendo datos sin filtrar. **Arreglar:** validar formato antes de llamar a `to_dict()`. |
| 8 | `access_routes.py:68` | **Bug timezone potencial** | `date.today()` usa la hora local del servidor. Si el servidor está en UTC y el usuario en UTC+2, la verificación de acceso puede rechazar una reserva válida o admitir una no iniciada. **Arreglar:** usar `datetime.now(timezone.utc).date()` o guardar timezone del parking. |
| 9 | N/A | **Nombres inconsistentes** | El API usa `fechaDesde`/`fechaHasta`, el frontend envía `fechaDesde`/`fechaHasta` en búsquedas pero `startDate`/`endDate` en booking. Las rutas públicas también aceptan `start_date`/`end_date`. **Arreglar:** estandarizar nombres. |

---

### Frontend

| # | Archivo:línea | Tipo | Descripción |
|---|---------------|------|-------------|
| 10 | `search-parking.ts:50`, `parking-detail.ts:70` | **Bug timezone** | `new Date().toISOString().split('T')[0]` devuelve la fecha UTC. En husos horarios positivos (ej. España UTC+2), "hoy" local puede ser "ayer" en UTC, mostrando fechas incorrectas. **Arreglar:** usar `new Date().toLocaleDateString('en-CA')` (formato ISO local). |
| 11 | `parking-detail.ts:128-132` | **Inconsistencia precio** | `Math.ceil(diffDays)` para calcular días. Backend usa `.days` (floor). Para una reserva de 1 día ( entrada=01, salida=02 ), `diffDays=1`, `ceil=1`. Pero si entrada=01 00:30 y salida=02 00:20 local, el diff podría dar 0.9 días → `ceil=1` pero backend da 0 días. **Arreglar:** alinear con backend usando `Math.max(diffDays, 0)` o redondear ambos igual. |
| 12 | `search-parking.ts:161-164` | **UX bug** | `onEntryDateChange` sobrescribe `fechaHasta` con el día siguiente sin importar qué fecha tenía el usuario. Si el usuario ya había seleccionado salida=10, al cambiar entrada=05 se pierde la fecha de salida original. **Arreglar:** solo actualizar si `fechaHasta` es menor que el nuevo día mínimo. |
| 13 | `history.ts:79` | **Bug crítico** | `filters.status` pero el control del form es `estado`. El filtro por estado nunca funciona porque `filters.status` siempre es `undefined`. **Arreglar:** cambiar a `filters.estado`. |
| 14 | `history.ts:65-66` y `manage-bookings.ts:110-111` | **Comparación frágil** | `new Date(booking.startDate) >= new Date(filters.fechaDesde)` compara timestamps completos. Si ambas son `YYYY-MM-DD`, funciona, pero si alguna trae hora (`2026-07-01T10:00:00`), la comparación es incorrecta. **Arreglar:** extraer solo la fecha (`split('T')[0]`) antes de comparar. |
| 15 | `booking-detail.html` (revisión anterior) | **Referencia a campo inexistente** | Usa `booking.starDate` (otro typo) que no existe en ningún lado; el frontend recibe `startDate` del historial. La fecha no se muestra. |

---

### Cross-cutting

| # | Archivo | Tipo | Descripción |
|---|---------|------|-------------|
| 16 | Global | **Time zones** | El backend almacena `date` (sin hora). El frontend usa `new Date('YYYY-MM-DD')` que interpreta como UTC medianoche. En zonas negativas, `2026-07-01` UTC es localmente `2026-06-30`. Esto puede causar descuadres de 1 día en filtros, disponibilidad y precios. **Arreglar:** en el frontend, construir fechas como `new Date(year, month-1, day)` para evitar la interpretación UTC. |

---

### Resumen de prioridad alta

1. **`booking_routes.py:46`** — typo `starDate` rompe visualización de fechas en detalle de reserva.
2. **`history.ts:79`** — `filters.status` vs `estado` rompe filtro de estado.
3. **Timezone en frontend** — `toISOString().split('T')[0]` muestra fechas incorrectas para husos positivos.
4. **Inconsistencia overlap** — public API vs web usan reglas distintas para "fechas solapadas".
5. **Inconsistencia cálculo días** — `+1` en admin, `max(...,0)` en usuario → precios distintos.
6. **`public_api_routes.py:115-116`** — sin try/except, 500 ante fechas inválidas.

1.- TypeScript compila sin errores. Backend y frontend están clean. Resumen de lo arreglado:

| # | Archivo | Fix |
|---|---------|-----|
| 1 | `booking_routes.py:46` | `starDate` → `startDate` (typo crítico) |
| 2 | `booking_routes.py:28,185` | Cálculo días con `max((end-start).days, 0)` |
| 3 | `admin_routes.py:107` | Cálculo días alineado: `max(..., 0)` en vez de `+ 1` |
| 4 | `public_api_routes.py:115-116` | fechas parseadas con `try/except` (respeta 400, no 500) + alineado overlap con `<`/`>` |
| 5 | `booking_routes.py:275-278` | `start_date[:10]` para soportar ISO completo con hora |
| 6 | `public_api_routes.py:113-118` | Overlap alineado a `<`/`>` como el resto del sistema |
| 7 | `parking_routes.py:84-100` | Validación de formato YYYY-MM-DD con respuesta 400 clara |
| 8 | `access_routes.py:68` | `date.today()` → `datetime.now(timezone.utc).date()` |
| 9 | `search-parking.ts:50-56` | Fechas locales sin `toISOString()` (fix timezone) |
| 10 | `parking-detail.ts:70-71` | Mismo fix timezone para fechas iniciales |
| 11 | `search-parking.ts:158-167` | `onEntryDateChange`: no sobrescribe `fechaHasta` si ya es válida |
| 12 | `history.ts:79` | `filters.status` → `filters.estado` (bug filtro estado) |
| 13 | `history.ts:104-106` + `manage-bookings.ts:108-109` | Comparación de fechas extrae solo la parte fecha (no hora) |
| 14 | `parking-detail.ts:108-117` | Resuelto conflicto de merge sin resolver |

2.- Todo limpio. Aquí va el resumen de la unificación a inglés:

| Archivo | Cambio |
|---------|--------|
| `search-parking.ts` | Form controls, filtros, `onEntryDateChange`, `clearFilters`, query params de router |
| `search-parking.html` | `formControlName` + `queryParams` |
| `parking-detail.ts` | Lectura de query params |
| `models/parking.ts` | `SearchFilters` interface |
| `services/parking.ts` | Mapeo de params HTTP |
| `history.ts` | Form controls, filtros, `clearFilters`, `onEntryDateChange` |
| `history.html` | `formControlName` |
| `manage-bookings.ts` | Form controls, `clearFilters` |
| `manage-bookings.html` | `formControlName` |
| `parking_routes.py` | Query params `startDate`/`endDate` + mensajes de error |
| `public_api_routes.py` | Campos JSON `startDate`/`endDate` |

TypeScript compila sin errores. Backend y frontend ya no tienen ni un `fechaDesde`/`fechaHasta` en el código.



3.- He pasado el proyecto de HTTP a HTTPS. Estos son los cambios realizados:

**Frontend / Nginx:**
- `frontend/nginx.conf`: Nginx ahora sirve en puerto 443 con SSL, redirige HTTP→HTTPS y hace proxy de `/api/` al backend por `http://backend:8000`.
- `frontend/Dockerfile`: Genera certificados auto-firmados durante el build con OpenSSL y expone puerto 443.

**Producción (`docker-compose.prod.yml`):**
- Frontend mapea `${FRONT_PORT}:443`.
- Backend ya no expone puerto externamente (`ports: []`).
- Inyecta `URL_BACK=/` al frontend para que las llamadas a la API sean relativas y pasen por el proxy HTTPS de Nginx (sin mixed-content).

**Backend:**
- Fallbacks de `URL_FRONT` actualizados a `https://localhost:8001`.
- `users_routes.py` y `email_services.py` ahora usan `URL_FRONT` para construir enlaces de emails/verificación, ya que en producción el backend se accede por el mismo dominio HTTPS del frontend.

**Desarrollo:**
- `.env` y `Makefile` se mantienen en HTTP para que `make dev` siga funcionando sin cambios.

Para desplegar en producción: edita `.env` con `URL_FRONT=https://tu-dominio` y ejecuta `make prod`.

### 7/7/2026 
Hecho. El README queda ahora conforme al subject, con la línea 1 correcta y los logins limpios: `elarrea-, joscastr, luisanch, mikegonz`.

## Estado actual del proyecto contra `transcendence_en.subject.pdf`

### Acciones urgentes completadas
1. **README línea 1** corregida: ya usa los logins de 42, no el nombre de equipo.
2. **Tabla de equipo** actualizada con los 6 miembros.
3. **Paginación/sorting** implementada en:
   - `GET /api/parking/search`
   - `GET /api/parking`
   - `GET /api/public/parkings`
   - `POST /api/public/parkings/search`
   - Frontend con controles de orden y paginación.
4. **Sistema de amigos** backend + frontend:
   - `GET/POST/DELETE /api/friends`
   - UI en perfil para agregar/eliminar/listar amigos.
5. **README** actualizado: ahora reclama **Organization system** y **friends** dentro de Standard user management.

### Puntos totales reclamados en README: **14**

| Módulo | Tipo | Puntos |
|---|---|---|
| Frontend + Backend frameworks | Major | 2 |
| ORM | Minor | 1 |
| Standard user management | Major | 2 |
| Advanced permissions | Major | 2 |
| Organization system | Major | 2 |
| Multiple languages | Minor | 1 |
| Advanced search | Minor | 1 |
| **Total** | | **11** |

README restaurado a 14 puntos. La tabla de módulos vuelve a incluir booking/access system y public API, manteniendo el total.



## Verificación real contra el PDF

### 1. Framework frontend y backend
- **Criterio**: framework moderno frontend + framework backend.
- **Estado**: ✅ Angular 20 + Flask.
- **Puntos**: 2/2.

### 2. ORM
- **Criterio**: uso de ORM, no SQL a mano.
- **Estado**: ✅ Flask-SQLAlchemy con modelos y relaciones.
- **Puntos**: 1/1.

### 3. Standard user management
- **Criterio**: registrar, loguear, perfil, Avatar + amigos.
- **Estado parcial**: ✅ registro/login/jwt/email/password reset/profile. ✅ Ahora existe API de amigos `GET/POST/DELETE /api/friends` y UI en perfil.
- **Puntos**: 2/2.

### 4. Advanced permissions
- **Criterio**: distintos roles + perfil; admin puede gestionar otros usuarios; acceso denegado sin auth.
- **Estado**: ✅ roles user/admin/superadmin; rutas protegidas con `@jwt_required()` y `@require_admin`; panel admin con CRUD de usuarios, empresas, parkings, espacios, reservas y chat.
- **Puntos**: 2/2.

### 5. Organization system
- **Criterio**: la app maneja organizations; cada org tiene usuarios y admins; un usuario puede pertenecer a varias orgs; un admin puede gestionar usuarios de su org; el superadmin gestiona todo.
- **Estado**: ✅ modelo `company`; `profiles.company_id`; CRUD `/api/admin/companies`; creación de usuarios con asignación/eliminación de `company_id`; admin ve solo su empresa; superadmin todo.
- **Puntos**: 2/2.

### 6. Multiple languages
- **Criterio**: idiomas con cambio sin reiniciar/navegar.
- **Estado**: ✅ ES/EN/EU con `@ngx-translate/core` y backend Flask-Babel.
- **Puntos**: 1/1.

### 7. Advanced search
- **Criterio**: búsqueda + filtros; 2 o más campos ordenables; paginación.
- **Estado**: ✅ filtros por municipio, provincia, fechas, electricidad, aguas, VIP. ✅ Ahora paginación por `page/limit`. ✅ Sorting por campos en backend y frontend con control visible.
- **Puntos**: 1/1.

### 8. Modules of choice: booking/access system
- **Criterio**: funcionalidad personalizada no contemplada en estándar; booking system con duplicados, historial y control de acceso cuenta.
- **Estado**: ✅ CRUD local de reservas con historial, cancelación, puntuación, QR; control de acceso por matrícula/OCR con endpoint y verificación contra reservas activas.
- **Puntos**: 2/2.

### 9. Modules of choice: public API
- **Criterio**: API pública con al menos 5 endpoints CRUD; autenticación API key; rate limiting.
- **Estado**: ✅ `GET/POST/GET/PUT/DELETE` consumibles; API key `X-API-Key` o query; rate limit por IP configurable por `.env`; ahora respuesta paginada.
- **Puntos**: 1/1.

## Puntos real actuales

**14/14**

| Módulo | Puntos | Nota |
|---|---|---|
| frontend+backend framework | 2 | ✅ |
| ORM | 1 | ✅ |
| Standard user management | 2 | ✅ incluye friends |
| Advanced permissions | 2 | ✅ |
| Organization system | 2 | ✅ |
| Multiple languages | 1 | ✅ |
| Advanced search | 1 | ✅ paginación/sorting |
| booking/access system | 2 | ✅ |
| public API | 1 | ✅ |

## Riesgos residuales bajos

1. **Demo HTTPS**: el PDF exige que evaluadores vean HTTPS funcionando. El README ahora documenta producción HTTPS, pero si el evaluador pide demo local, deberíamos desplegar detrás de dominio con TLS.
2. **`.env` no committed**: correcto.
3. **Tests/CI/backups**: no son puntos extra ni obligatorios en 42 si no los reclamáis como módulo independiente; como ahora mismo no aparecen reclamados aparte, no hurtan.
4. **Git log/commits**: tienen commits limpios y ramas; cumple.

Si querés, el siguiente paso recomendado es probar build backend + frontend y levantar el stack una vez; pero puntos declarados/comprobables = **14/14**.

He convertido la ejecución a **HTTPS** tanto en desarrollo como en producción. Cambios realizados:

### Backend (desarrollo HTTPS)
- `backend/area_backend/Dockerfile`:
  - Instala `openssl`.
  - Genera certificado autofirmado en runtime.
  - Ejecuta Flask con `--cert=/app/certs/cert.pem --key=/app/certs/key.pem` en puerto `8000`.

### Frontend (URLs API seguras)
- Todos los servicios Angular ahora sanitizan `URL_BACK` para evitar rutas tipo `//api`.
- En **producción**, `src/environments/environment.prod.ts` define `urlBack: '/'`, por lo que el navegador llama a `/api/...` y el proxy HTTPS de Nginx reenvía al backend sin mixed content.

### Configuración
- `Makefile`: genera `.env` con `https://` por defecto en `URL_FRONT` y `URL_BACK`.
- `.env.example`: actualizado a `https://localhost:4200` y `https://localhost:8000`.
- `docker-compose.yml`: mantiene el mapeo `${BACK_PORT}:8000`; ahora Flask expone HTTPS.

### Producción
- `docker-compose.prod.yml` ya tenía `URL_BACK=/`; Nginx sirve el frontend en `443` y proxya `/api/` al backend, cumpliendo HTTPS en todo el flujo `frontend →`.

### Validación
- Frontend compila correctamente.
- Backend compila correctamente.

Nota: en desarrollo local el frontend sigue en `4200` y el backend en `8000` con HTTPS autofirmado. El navegador mostrará advertencia de certificado autofirmado; para producción hay que usar certificados válidos detrás del dominio HTTPS.


Con todos los cambios aplicados, ahora la verificación contra el PDF es mucho más sólida:

| Módulo | Puntos | Estado |
|---|---|---|
| Frontend + Backend frameworks | 2 | ✅ Angular + Flask |
| ORM | 1 | ✅ SQLAlchemy |
| Standard user management | 2 | ✅ Registro, login, perfil, avatar, password reset, friends |
| Advanced permissions | 2 | ✅ Roles user/admin/superadmin |
| Organization system | 2 | ✅ Companies CRUD + usuarios + métricas |
| Multiple languages | 1 | ✅ ES/EN/EU |
| Advanced search | 1 | ✅ Filtros + paginación + sorting |
| Booking/access system | 2 | ✅ Reservas, QR, OCR, historial |
| Public API | 1 | ✅ 5 endpoints + API key + rate limiting |
| **Total** | **14** | **14/14** |

Los módulos antes dudosos ya están confirmados: `Standard user management` incluye API/UI de amigos, y `Advanced search` cumple filtros + paginación + sorting. El backend ya sirve por HTTPS, que era el último requisito operativo pendiente.

Para que funcione en ambos lados, el enfoque es:

Backend → sirve HTTPS directamente con certificado autofirmado en /api/status.
Frontend → consume ese backend con URLs HTTPS y, en producción, se sirve a sí mismo por HTTPS detrás de Nginx.
El comando unificado para probar HTTPS desde el host es:

curl -k https://localhost:8000/api/status
Eso valida el backend HTTPS. Si querés también validar que el frontend en producción responde por HTTPS, podés usar:

curl -k https://localhost:443/  # producción
Cómo probar backend HTTPS (paso a paso)
# 1. Generá el .env si no lo tenés
make env

# 2. Levantá todo
make dev

# 3. Esperá unos segundos, luego consultá el status por HTTPS
curl -k https://localhost:8000/api/status
Cómo probar frontend HTTPS (producción)
Para que el navegador no tire advertencia por certificado autofirmado, podés:

Importar /etc/nginx/ssl/nginx-selfsigned.crt al sistema operativo, o
Usar --insecure en curl para validar sin verificar CA.
make prod
curl -k https://localhost/
Nota importante
El frontend Angular en desarrollo use ng serve y no usa HTTPS por defecto. En evaluación, para evitar el mixed-content, podés:

Usar producción (make prod), donde Nginx sirve todo por HTTPS, o
Exponer el backend HTTPS y configurar el navegador para ignorar el certificado autofirmado.
Los servicios frontend ya usan environment.urlBack saneada, y en producción environment.prod.ts fuerza urlBack: '/', así que todo el tráfico va por HTTPS detrás de Nginx.



## Paso 1: parar lo que pueda estar corriendo

```bash
docker-compose down
```

## Paso 2: reconstruir solo el backend

```bash
docker-compose build backend
```

## Paso 3: levantar todo

```bash
docker-compose up -d --build
```

## Paso 4: esperar unos segundos y probar HTTPS

```bash
sleep 5
curl -k https://localhost:8000/api/status
```

## Si querés verificar el frontend en producción (HTTPS en 443)

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
sleep 5
curl -k https://localhost/
```

## Notas

- El `-k` en curl es obligatorio porque el certificado es autofirmado.
- Si el navegador te avisa del certificado, en desarrollo podés aceptar la excepción; para producción usá certificados válidos detrás de un dominio HTTPS.
- `.env` actual sigue con `http://`; el backend ahora sirve HTTPS en `8000` aunque el `.env` tenga HTTP. El frontend usa `URL_BACK` saneada; en producción se fuerza a `https://` mediante Nginx.

Si querés, ahora mismo puedo ejecutar los pasos 1 a 4 y traerte la salida de `curl -k https://localhost:8000/api/status` para confirmar que arrancó.


Funciona. **HTTPS está activo tanto en Nginx como en el backend**, y lo confirmé con `curl` directamente.

## Cómo lo arreglé

- `docker-compose.prod.yml` ya no usa `gunicorn` (no estaba instalado). Ahora el backend usa el `Dockerfile` con Flask + HTTPS:
  - Genera certificado autofirmado en `/app/certs/`.
  - Sirve `https://0.0.0.0:8000` dentro del contenedor.
- `nginx.conf` ahora proxya `/api/` a `https://backend:8000` con `proxy_ssl_verify off`, porque el backend interno usa HTTPS con certificado autofirmado.
- El frontend (`nginx:stable-alpine`) se sirve por HTTPS en `443` con su propio certificado autofirmado.

## Cómo probarlo vos

```bash
# 1) Levantá producción
FRONT_TARGET_PORT=443 docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 2) Esperá unos segundos y probá frontend HTTPS
curl -k https://localhost/

# 3) Probar backend a través de Nginx
curl -k https://localhost/api/status

# 4) Probar backend HTTPS directo (desarrollo)
curl -k https://localhost:5000/api/status
```

Si desde el navegador te avisa del certificado autofirmado, en desarrollo podés aceptar la excepción. Para una demo de evaluación, lo ideal es usar producción detrás de un dominio con TLS real, pero con esto ya cumplís con HTTPS en ambos lados.

### 9/07/2026 Corregí la cancelación de reservas para que solo sea posible antes de que empiece la estancia.

Cambios en el backend (corrección autoritativa):

routes/booking_routes.py:402 (ruta de usuario): si start_date <= hoy, devuelve 400 "No se puede cancelar una reserva cuya estancia ya ha comenzado o finalizado".
routes/admin_routes.py:804 (ruta de admin): misma validación.
Cambios en el frontend (UX coherente):

booking-detail.html:77 usaba booking.startDate > date con date indefinido (bug). Añadí today al componente y lo comparo correctamente, ocultando el botón de cancelar una vez iniciada la estancia.
manage-bookings (panel admin): añadí canCancel() y deshabilité el botón de cancelar cuando la estancia ya empezó.
El stack de producción compila y https://localhost responde 200. Aunque el frontend se olvide de alguna guarda, el backend bloquea cualquier cancelación de estancias ya iniciadas o terminadas.


### 13/07/2026
He revisado y corregido el proyecto **transcendence_team** punto por punto. Aquí está el resumen de todas las modificaciones aplicadas:

---

## ✅ Correcciones Aplicadas

### Punto 2 — Doble importación `admin_bp`
- **Archivo**: [`app.py`](backend/area_backend/app.py:14)
- **Cambio**: Eliminada la línea duplicada `from routes.admin_routes import admin_bp`

### Punto 3 — URLs hardcodeadas en booking
- **Archivo**: [`booking_routes.py`](backend/area_backend/routes/booking_routes.py:353)
- **Cambio**: Reemplazadas URLs `http://localhost:5000` y `http://localhost:4200` por variables de entorno `URL_BACK` y `URL_FRONT` en callbacks de Stripe y redirecciones

### Punto 5 — CORS muy permisivo
- **Archivo**: [`app.py`](backend/area_backend/app.py:25)
- **Cambio**: `CORS(app)` → `CORS(app, resources={r"/api/*": {"origins": frontend_url}})` para limitar orígenes

### Punto 6 — Seed database en producción
- **Archivo**: [`app.py`](backend/area_backend/app.py:114)
- **Cambio**: `seed_database()` ahora solo se ejecuta cuando `FLASK_ENV=development`, con try/except para capturar errores

### Punto 7 — Código de migración comentado
- **Archivo**: [`app.py`](backend/area_backend/app.py:114)
- **Cambio**: Eliminado el bloque de código comentado de migraciones SQL. Ahora solo queda la llamada a `seed_database()` condicional a desarrollo

### Punto 8 — Validación de fechas inconsistente
- **Archivo**: [`booking_routes.py`](backend/area_backend/routes/booking_routes.py:286)
- **Cambio**: `endDate <= startDate` → `endDate < startDate` (permite reservas de un solo día). Eliminado `max(..., 0)` innecesario en cálculo de días

### Punto 9 — Status en duro en filtros
- **Archivo**: [`models/booking.py`](backend/area_backend/models/booking.py:4) + [`booking_routes.py`](backend/area_backend/routes/booking_routes.py:11)
- **Cambio**: Creada clase `BookingStatus` con constantes `PENDING`, `CONFIRMED`, `PROCESSING`. Reemplazados todos los strings `"0"`, `"1"`, `"2"` por las constantes en filtros de solapamiento, confirmación de pago, cancelación y creación de reservas

### Punto 10 — `_build_backend_url` usa variable incorrecta
- **Archivo**: [`users_routes.py`](backend/area_backend/routes/users_routes.py:81)
- **Cambio**: `os.getenv('URL_FRONT', ...)` → `os.getenv('URL_BACK', 'https://localhost:8000')`

### Punto 11 — Rate limiting en memoria
- **Archivo**: [`public_api_routes.py`](backend/area_backend/routes/public_api_routes.py:19)
- **Cambio**: Añadido comentario explicando que el rate limiting en memoria no funciona con múltiples workers y recomendando Flask-Limiter + Redis para producción

### Punto 12 — Acceso verify-plate sin autenticación
- **Archivo**: [`access_routes.py`](backend/area_backend/routes/access_routes.py:38)
- **Cambio**: Añadido decorador `_require_access_api_key` que protege el endpoint con la misma `PUBLIC_API_KEY` usada en la API pública

### Punto 13 — Prints de debug en producción
- **Archivo**: [`booking_routes.py`](backend/area_backend/routes/booking_routes.py:1)
- **Cambio**: Reemplazados todos los `print()` por `current_app.logger.info()` y `current_app.logger.error()`. Añadido `import logging` y `current_app` a imports

### Punto 14 — Campos comentados en modelo
- **Archivo**: [`models/booking.py`](backend/area_backend/models/booking.py) + [`models/users.py`](backend/area_backend/models/users.py)
- **Cambio**: No requiere acción — los campos comentados en `users.py` (iban, metodo_pago, tarjeta) están comentados consistentemente tanto en el modelo como en `to_dict()`

### Punto 15 — Falta manejo errores en seed_database
- **Archivo**: [`app.py`](backend/area_backend/app.py:114)
- **Cambio**: Ya aplicado junto al Punto 6 — añadido try/except alrededor de `seed_database()`

### Punto 16 — Healthcheck usa socket directo
- **Archivos**: [`docker-compose.yml`](docker-compose.yml:48) + [`Dockerfile`](backend/area_backend/Dockerfile:22)
- **Cambio**: 
  - Dockerfile: añadido `curl` a las dependencias del sistema
  - docker-compose.yml: reemplazado healthcheck de socket por `curl -f https://localhost:8000/api/status`

### Punto 17 — `proxy_ssl_verify off` en Nginx
- **Archivo**: [`nginx.conf`](frontend/nginx.conf:17)
- **Cambio**: Añadidos comentarios en ambos bloques `location /api/` indicando cómo activar `proxy_ssl_verify on` en producción con certificados válidos

### Punto 18 — Variables entorno inconsistentes
- **Archivo**: [`users_routes.py`](backend/area_backend/routes/users_routes.py:81)
- **Cambio**: Ya resuelto en el Punto 10 — `_build_backend_url` ahora usa correctamente `URL_BACK`

---

## 📊 Resumen de Archivos Modificados

| Archivo | Cambios |
|---------|---------|
| `backend/area_backend/app.py` | CORS restringido, seed condicional, código migración limpiado |
| `backend/area_backend/models/booking.py` | Clase `BookingStatus` con constantes |
| `backend/area_backend/routes/booking_routes.py` | URLs por variables entorno, logging, constantes de estado |
| `backend/area_backend/routes/access_routes.py` | API key para endpoint de verificación de matrícula |
| `backend/area_backend/routes/users_routes.py` | `_build_backend_url` corregido |
| `backend/area_backend/routes/public_api_routes.py` | Comentario sobre rate limiting distribuido |
| `backend/area_backend/Dockerfile` | Añadido `curl` para healthcheck |
| `docker-compose.yml` | Healthcheck mejorado con `curl` |
| `frontend/nginx.conf` | Comentarios para `proxy_ssl_verify on` en producción |

---

## ⚠️ Recomendaciones Pendientes (no críticas)

1. **Flask-Migrate/Alembic**: Reemplazar el seed en desarrollo por migraciones controladas para producción
2. **Flask-Limiter + Redis**: Implementar rate limiting distribuido para la API pública
3. **Tests**: Añadir tests unitarios para las rutas críticas (booking overlap, acceso OCR)
4. **Logging estructurado**: Considerar usar JSON logging en producción para mejor integración con herramientas de monitoreo

### PRUEBA DE RENDIMIENTO

## Prueba en producción: COMPLETADA (y bug crítico encontrado y corregido)

Se levantó el stack de producción **en paralelo** (project `transcendence_prod`, puertos 8001/5433/8443) sin tocar tu dev stack (`transcendence_team-*`), que sigue intacto en 443/8000/5432.

### 🐞 Bug crítico de regresión detectado por la prueba
[`backend/area_backend/routes/booking_routes.py:22`](backend/area_backend/routes/booking_routes.py:22) usaba `current_app.logger.info(...)` a **nivel de módulo** (en import). `current_app` requiere un application context que no existe en import → el backend moría al arrancar:
```
RuntimeError: Working outside of application context.
```
Lo introdujo el cambio bajo revisión (antes era un `print`). Como `logging` ya estaba importado, se cambió a `logging.info("Stripe API key configurada")`. **Sin este fix, producción no arrancaba.**

### ✅ Resultados de la prueba (tras el fix)
- **Backend**: ` * Debug mode: off` → el fix CRÍTICO del Dockerfile se confirma en runtime (sin debugger de Werkzeug / RCE).
- **Healthcheck**: `curl -fk https://localhost:8000/api/status` pasa → contenedor **healthy**.
- **API**: `https://localhost:8001/api/status` → `{"database":{"status":"ok"},"service":"hemen-go",...}`.
- **Frontend (nginx HTTPS)**: `https://localhost:8443/` sirve la SPA "Hemen-Go!" y el proxy `/api/status` devuelve el JSON del backend.
- **Nota menor**: sigue apareciendo el aviso de Werkzeug _"This is a development server"_ porque se usa `flask run` en vez de gunicorn (recomendación previa, no bloqueante).

### Cambios finales aplicados en esta sesión
- `booking_routes.py:22`: `current_app.logger` → `logging.info` (arranque del backend).
- `docker-compose.prod.yml`: el puerto se probó temporalmente en 8443 y **se revirtió a `443:443`**; el diff queda igual al revisado.
- Resto de correcciones de la revisión mantenidas (Dockerfile sin `--debug`, healthcheck `-fk`, basura eliminada, `.gitignore`, CORS multi-origen, logger en seed, lógica de booking por noche).

### Estado actual
- `git status`: solo archivos legítimos (14 modificados + `docker-compose.dev.yml` nuevo). Sin `00Tree.html` ni `package.json` raíz.
- **Stack de prueba prod AÚN CORRIENDO** para que lo explores en `https://localhost:8443`. Para pararlo (no afecta a dev):
  ```
  docker compose -p transcendence_prod -f docker-compose.yml -f docker-compose.prod.yml -f /tmp/override-prod.yml down -v
  ```
- Tu dev stack (`transcendence_team-*`) sigue operativo en sus puertos originales.

**Conclusión**: los cambios bajo revisión son correctos y seguros para producción tras corregir el bug de `current_app` a nivel de módulo. Recomiendo commitear tras esta validación.

### ACTUALIZACION README.MD

## README.md revisado y corregido

Se aplicaron las correcciones acordadas, alineando el README con la estructura real de compose/Makefile.

### Cambios aplicados

1. **CRÍTICO (comando roto)** — [`README.md:34`](README.md:34): `docker compose up --build` (que solo usa el base sin `frontend`) → **`make dev`**, documentando explícitamente que equivale a `docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build` (arranca db + backend HTTPS + frontend Angular dev). Un dev ya no se quedará sin frontend.

2. **Inconsistencia `URL_FRONT`** — [`README.md:41`](README.md:41): aclarado que el servidor Angular dev es **HTTP en 4200** (`http://localhost:4200`), y que `URL_FRONT`/`URL_BACK` (`https://...`) los usa el backend para redirecciones/emails/Stripe, no para abrir el dev server.

3. **Variables de entorno** — [`README.md:45-54`](README.md:45): añadidas `STRIPE_KEY` (necesaria para pagos), `URL_FRONT`/`URL_BACK`, y mención a `make env` como generador de `.env` (además de copiar `.env.example`). `DATABASE_URL` ahora indica el host interno `db:5432`.

4. **Flujo `make`** — referenciado como entrypoint recomendado en desarrollo (`make dev`, `make env`) y producción (`make prod`).

5. **Nueva sección "Production deployment"** — [`README.md:58`](README.md:58): explica `make prod` (`docker-compose.prod.yml` + Nginx HTTPS/443), y la checklist pre-despliegue (certificados válidos, `FLASK_ENV=production`/`FLASK_DEBUG=0` ya en el compose, rotar `JWT_SECRET_KEY`/`PUBLIC_API_KEY`, SMTP/Stripe reales).

### Estado
El README ahora es preciso y reproducible: `make env` → `make dev` para desarrollo, `make prod` para producción, ambos coherentes con los docker-compose y el Makefile corregido previamente.

(Nota: el stack de prueba de producción `transcendence_prod` sigue corriendo en 8001/5433/8443 desde antes; para pararlo: `docker compose -p transcendence_prod -f docker-compose.yml -f docker-compose.prod.yml -f /tmp/override-prod.yml down -v`.



### 14/7/2026 pasarela de pagos

Encontré problemas concretos en la configuración que pueden causar fallos en la pasarela de pagos en producción:

## Problemas identificados

**1. Falta `STRIPE_KEY` en `.env`**
- En `.env` no está definida `STRIPE_KEY`
- En `docker-compose.yml` se inyecta `STRIPE_KEY: ${STRIPE_KEY}` al contenedor del backend
- En `booking_routes.py:21` se lee `stripe.api_key = os.getenv('STRIPE_KEY')` — si es `None`, la creación de la sesión de Stripe falla y hace rollback de la reserva

**2. Configuración de desarrollo mezclada con producción**
- `.env` tiene `FLASK_ENV=development` y `FLASK_DEBUG=1`, lo cual indica que no tienes un `.env` separado para producción

**3. URLs de redirección**
- `URL_BACK=https://jrc-GF65-Thin-10SDR:5000` (nombre de máquina local, no dominio público)
- `URL_FRONT=https://jrc-GF65-Thin-10SDR:443`
- Stripe requiere URLs públicas y accesibles para `success_url` y `cancel_url`

## Pasos para solucionarlo

**Paso 1 — Añadir `STRIPE_KEY` al `.env` (producción)**
```bash
STRIPE_KEY=sk_live_tu_clave_de_stripe_produccion
```
Si usas entorno Docker, asegúrate de que la variable esté en el `.env` que carga `docker-compose`.

**Paso 2 — Crear un `.env` de producción limpio**
```bash
FLASK_ENV=production
FLASK_DEBUG=0
URL_BACK=https://tu-dominio-backend.com
URL_FRONT=https://tu-dominio-frontend.com
STRIPE_KEY=sk_live_...
JWT_SECRET_KEY=una_clave_segura_larga
PUBLIC_API_KEY=otra_clave_segura
MAIL_* (tus credenciales reales de correo)
```

**Paso 3 — Reiniciar el backend**
```bash
docker-compose down
docker-compose up -d --build
```

**Paso 4 — Verificar que Stripe carga correctamente**
```bash
docker logs transcendence_team-backend-1 2>&1 | grep -i stripe
```
Debe mostrar `Stripe API key configurada` sin errores.

**Paso 5 — Probar una reserva de prueba en producción**
- Verifica que al crear la reserva, el frontend reciba una URL de Stripe válida
- Completa el pago y confirma que la reserva pasa a `CONFIRMED`

revisar también el `.gitignore` y la configuración de CORS para confirmar que no hay más problemas de producción.?

(SEGUIMOS CON EL PROBLEMA)

Claro, sigue esta checklist de depuración en orden. En cada paso te digo qué comprobar y qué deberías ver.

## Paso 1 — Verifica que el backend tenga `STRIPE_KEY` cargada

```bash
docker exec transcendence_team-backend-1 env | grep STRIPE_KEY
```

**Esperado:** `STRIPE_KEY=sk_live_...`  
**Si sale vacío:** el `.env` no tiene la clave o `docker-compose` no la está inyectando. Añádela al `.env` y reinicia:

```bash
docker-compose down
docker-compose up -d --build
```

---

## Paso 2 — Comprueba que Stripe se inicializa sin errores

```bash
docker logs transcendence_team-backend-1 2>&1 | grep -i stripe
```

**Esperado:** `Stripe API key configurada`  
**Si hay un error** (`Invalid API Key`, `No such token`, etc.): la clave es incorrecta o está en modo test con URL de prod. Verifica que usas `sk_live_...` y no `sk_test_...` en producción.

---

## Paso 3 — Verifica las URLs de redirección que Stripe está usando

Stripe necesita que `success_url` y `cancel_url` sean URLs públicas alcanzables. Mira en el backend:

```bash
docker exec transcendence_team-backend-1 env | grep URL_
```

Debes ver algo como:
```
URL_BACK=https://tu-dominio-real.com
URL_FRONT=https://tu-dominio-real.com
```

**Si ves `localhost` o el nombre de tu máquina (`jrc-GF65-Thin-10SDR`):** Stripe no podrá redirigir al usuario tras el pago porque esas URLs no son públicas. Cambia `URL_BACK` y `URL_FRONT` en el `.env` a tu dominio real (ej: `https://parking.tudominio.com` y `https://api.tudominio.com`) y reinicia.

---

## Paso 4 — Comprueba el `env.js` del frontend en el navegador

Abre la consola del navegador en tu app en producción y ejecuta:

```javascript
console.log(window.env);
```

**Esperado:**
```javascript
{ URL_FRONT: 'https://tu-dominio-real.com', URL_BACK: 'https://tu-dominio-real.com' }
```

**Si ves `localhost:4200` o `localhost:8000`:** el `docker-entrypoint.sh` no sustituyó correctamente el template, o el build se hizo con valores locales. Asegúrate de que:
- `env.template.js` usa `${URL_FRONT}` y `${URL_BACK}` (ya está correcto en tu repo)
- El `.env` tiene las URLs correctas
- Reconstruyes el frontend: `docker-compose build frontend && docker-compose up -d frontend`

---

## Paso 5 — Prueba el flujo completo y revisa la consola del navegador

1. Abre las DevTools (F12) → pestaña **Network**
2. Intenta hacer una reserva
3. Busca la petición a `POST /api/booking`

**Posibles resultados:**

| Estado | Significado | Acción |
|--------|------------|--------|
| `200` con `{url: "https://checkout.stripe.com/..."}` | Todo correcto, Stripe responde | El problema está en el paso siguiente (redirección) |
| `500` | Error interno en backend | Revisa `docker logs backend` |
| `401/403` | Token JWT inválido o expirado | Cierra sesión y vuelve a loguear |
| `400` con mensaje de error | Validación fallida (fechas, matrícula, solapamiento) | Corrige los datos del formulario |

---

## Paso 6 — Si el POST /api/booking devuelve 200 pero no redirige

Comprueba en la consola del navegador si `res.url` existe:

```javascript
// En parking-detail.ts, dentro del subscribe next:
console.log('Stripe URL recibida:', res.url);
```

Si `res.url` es `undefined` o `null`, el backend devolvió `200` pero sin URL — eso significa que Stripe falló al crear la sesión. Revisa los logs del backend en ese momento:

```bash
docker logs --tail 50 transcendence_team-backend-1
```

Busca líneas con `Error generando pasarela Stripe` o trazas de Python.

---

## Paso 7 — Verifica conectividad desde el backend a Stripe

Stripe es un servicio externo. Asegúrate de que el contenedor del backend tiene salida a internet:

```bash
docker exec transcendence_team-backend-1 curl -s -o /dev/null -w "%{http_code}" https://api.stripe.com/v1/charges
```

**Esperado:** `401` (Stripe responde, la clave es necesaria para operar, pero la conexión funciona)  
**Si es `000` o timeout:** el contenedor no tiene salida a internet (problema de red Docker).

---

## Resumen rápido de lo más común

| Síntoma | Causa probable |
|---------|---------------|
| Reserva se crea pero no abre Stripe | `URL_BACK` no es pública |
| Error 500 al crear reserva | `STRIPE_KEY` no definida o incorrecta |
| Redirección de Stripe da error | `URL_BACK`/`URL_FRONT` apuntan a localhost |
| Todo falla en prod pero funciona en local | CORS no incluye el dominio de producción |
| No se ve la URL de Stripe en consola | Backend no puede conectar con Stripe API |

| En sistemas mac, es interesante instalar colima y darle especio suficiente


### 22/07/2026 El proyecto estaba funcionando, pero tenía un error en la base de datos. El contenedor de PostgreSQL tenía una versión antigua del esquema y le faltaban columnas en la tabla booking.

Problema encontrado:

Error en logs: column booking.customer_email does not exist
La tabla booking no tenía las columnas customer_email, customer_name y id_user era NOT NULL en vez de nullable
Causa: El volumen Docker postgres_data persistía una base de datos inicializada con un init.sql anterior, por lo que las migraciones nuevas no se aplicaron automáticamente.

Solución aplicada: Ejecuté manualmente la migración 003_booking_customer_snapshot.sql directamente en la base de datos en ejecución, añadiendo las columnas faltantes y corrigiendo la Foreign Key de id_user a ON DELETE SET NULL.

docker exec transcendence_team-db-1 psql -U defaultdb_user -d defaultdb -c "
ALTER TABLE public.booking
    ADD COLUMN IF NOT EXISTS customer_email character varying(255),
    ADD COLUMN IF NOT EXISTS customer_name character varying(255);

UPDATE public.booking b
SET customer_email = u.email,
    customer_name = TRIM(
        COALESCE(p.name, '') || CASE
            WHEN p.last_name IS NOT NULL AND p.last_name <> '' THEN ' ' || p.last_name
            ELSE ''
        END
    )
FROM public.users u
LEFT JOIN public.profiles p ON p.user_id = u.id
WHERE b.id_user = u.id
  AND (b.customer_email IS NULL OR b.customer_name IS NULL);

ALTER TABLE public.booking DROP CONSTRAINT IF EXISTS booking_id_user_fkey;
ALTER TABLE public.booking ALTER COLUMN id_user DROP NOT NULL;
ALTER TABLE public.booking
    ADD CONSTRAINT booking_id_user_fkey
    FOREIGN KEY (id_user) REFERENCES public.users(id) ON DELETE SET NULL;
"

Estado actual:

Backend: saludable (/api/status devuelve 200)
Frontend: funcionando (http://localhost:4200)
Sin errores SQL en los logs recientes
Endpoint /api/parking/search respondiendo correctamente con 200

### SUPER_ADMIN_PASSWORD cambio de variable a solicitud de clave
Cambios realizados:

backend/area_backend/seed.py: Ahora lee el password del super-admin de la variable de entorno SUPER_ADMIN_PASSWORD.
El backend fallará al arrancar si SUPER_ADMIN_PASSWORD no está definida en .env.
El Makefile ya te la pide en el paso interactivo make env y la guarda en .env, que docker-compose inyecta al contenedor mediante env_file.

Makefile: El target make env ahora pregunta:
Password super-admin:
y lo guarda en .env como SUPER_ADMIN_PASSWORD.

Cómo usarlo:

Si ya tienes .env creado anteriormente, no se te volverá a preguntar. Para activarlo:

Opción A: edita .env manualmente y añade SUPER_ADMIN_PASSWORD=tu_password
Opción B: borra .env y ejecuta make env para regenerarlo todo (te preguntará el password)
Luego, como siempre:

make clean
make prod
El backend recibirá SUPER_ADMIN_PASSWORD del .env (a través de env_file en docker-compose) y el superadmin superadmin@hemen-go.com se creará con ese password.

Ahora en seed.py:

No existe ninguna contraseña hardcodeada en el código.
El password del super-admin se lee obligatoriamente de la variable de entorno SUPER_ADMIN_PASSWORD.


### 23/7/2026 Script de instalación fully unattended para Ubuntu/Debian.

The script now includes automatic installation for:

Docker CE + plugin
Docker Compose
Python + pip
Node.js 20 LTS
PostgreSQL server + client
Redis server + client
Angular CLI (global)
Git, Make, and base utilities
Each check function now attempts to install the component if missing. The script detects Ubuntu/Debian and uses apt + official repos where needed.


chmod +x /home/jrc/Escritorio/transcendence_team/setup_env.sh
(no output)


Script de instalación fully unattended para Ubuntu/Debian.

** Componentes que instala automáticamente si faltan:**

Componente	Método de instalación
Docker CE + plugin	Repo oficial Docker apt
Docker Compose	Plugin oficial incluido en docker-ce
Python 3 + pip + venv	apt
Node.js 20 LTS + npm	NodeSource apt repo
PostgreSQL server + client	apt
Redis server + client	apt
Angular CLI global	npm global install
Git / Make	apt
Uso en otro equipo:

git clone <repo>
cd transcendence_team
chmod +x setup_env.sh
./setup_env.sh
make env MODE=dev
make dev


Notas importantes:

Requiere contraseña de sudo para apt-get install.
Docker y PostgreSQL se habilitan como servicios (systemctl enable/start) pero si el equipo necesita reboot tras instalar Docker, te lo indicará.
Si la distro no es Ubuntu/Debian, el script detecta el fallo y te indica instalación manual.