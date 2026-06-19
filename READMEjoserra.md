
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

