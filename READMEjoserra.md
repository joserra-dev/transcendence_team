
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
      • En parking-detail.ts, restauré y amplié el bloqueo de reserva: ahora comprueba si el usuario tiene configurado un método de pago válido completo (IBAN válido,    
      Tarjeta válida, o Efectivo). Si no tiene ninguno, lo redirige al perfil para configurarlo antes de permitirle reservar.  

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
