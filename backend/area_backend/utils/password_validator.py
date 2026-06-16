# utils/validators.py
import re

import re

class PasswordValidator:
    # Expresión regular estándar (mín. 8 caracteres, 1 mayúscula, 1 minúscula, 1 número, 1 carácter especial)
    PASSWORD_REGEX = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

    @classmethod
    def validar(cls, password: str, email: str = "") -> tuple[bool, str]:
        """
        Valida si una contraseña cumple con los requisitos mínimos de seguridad.
        Evita el uso de la palabra 'password' y partes del email.
        Retorna un tuple: (is_valid, "mensaje de error o éxito")
        """
        if not password:
            return False, "La contraseña no puede estar vacía."
        
        # Pasamos a minúsculas para comparaciones insensibles a mayúsculas/minúsculas
        password_lower = password.lower()

        # 1. Validación: No contener la palabra 'password'
        if "password" in password_lower:
            return False, "La contraseña no puede contener la palabra 'password'."

        # 2. Validación: No contener el nombre de usuario del email
        if email and "@" in email:
            # Extraemos la parte anterior al @ (ej. "pruebamail" de "pruebamail@gmail.com")
            email_username = email.split("@")[0].lower()
            
            # Validamos si el username está dentro de la contraseña
            if email_username and email_username in password_lower:
                return False, "La contraseña no puede contener partes de tu correo electrónico."

        # 3. Validaciones de estructura clásica
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres."
            
        if not re.search(r"[A-Z]", password):
            return False, "La contraseña debe contener al menos una letra mayúscula."
            
        if not re.search(r"[a-z]", password):
            return False, "La contraseña debe contener al menos una letra minúscula."
            
        if not re.search(r"\d", password):
            return False, "La contraseña debe contener al menos un número."
            
        if not re.search(r"[@$!%*?&]", password):
            return False, "La contraseña debe contener al menos un carácter especial (@$!%*?&)."

        # Verificación del regex completo por seguridad final
        if not re.match(cls.PASSWORD_REGEX, password):
            return False, "La contraseña no cumple con el formato de seguridad requerido."

        return True, "Contraseña válida."