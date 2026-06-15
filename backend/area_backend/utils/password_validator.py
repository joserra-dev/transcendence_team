# utils/validators.py
import re

class PasswordValidator:
    # Standard regular expression (min. 8 characters, 1 uppercase, 1 lowercase, 1 number, 1 special character)
    PASSWORD_REGEX = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"

    @classmethod
    def validar(cls, password: str) -> tuple[bool, str]:
        """
        Validates if a password meets the minimum security requirements.
        Returns a tuple: (is_valid, "error or success message")
        """
        if not password:
            return False, "La contraseña no puede estar vacía."
        
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

        # Si pasa todos los filtros individuales, verificamos el regex completo por seguridad
        if not re.match(cls.PASSWORD_REGEX, password):
            return False, "La contraseña no cumple con el formato de seguridad requerido."

        return True, "Contraseña válida."