import re

class IdentityValidator:
    """Class responsible for validating official identification documents (DNI, NIE, CIF, and Foreign Passports)."""
    
    LETTER_MAPPING = "TRWAGMYFPDXBNJZSQVHLCKE"
    CIF_LETTER_CONTROL = "JABCDEFGHI"  # 0->J, 1->A, 2->B, etc.

    @classmethod
    def validate_dni(cls, dni: str) -> bool:
        """Validates a standard Spanish DNI (8 digits + 1 letter)."""
        dni = dni.strip().upper()
        if not re.match(r"^\d{8}[A-Z]$", dni):
            return False
            
        numbers = dni[:-1]
        letter = dni[-1]
        return cls.LETTER_MAPPING[int(numbers) % 23] == letter

    @classmethod
    def validate_nie(cls, nie: str) -> bool:
        """Validates a Spanish NIE (Letter X, Y, Z + 7 digits + 1 letter)."""
        nie = nie.strip().upper()
        if not re.match(r"^[XYZ]\d{7}[A-Z]$", nie):
            return False
            
        initial_mapping = {"X": "0", "Y": "1", "Z": "2"}
        initial_letter = nie[0]
        
        transformed_numbers = initial_mapping[initial_letter] + nie[1:-1]
        final_letter = nie[-1]
        
        return cls.LETTER_MAPPING[int(transformed_numbers) % 23] == final_letter

    @classmethod
    def validate_cif(cls, cif: str) -> bool:
        """Validates a Spanish CIF (Corporate Tax ID)."""
        cif = cif.strip().upper()
        if not re.match(r"^[ABCDEFGHJNPQRSTUVWXY]\d{7}[A-J0-9]$", cif):
            return False

        organization_letter = cif[0]
        digits = cif[1:-1]
        control_digit = cif[-1]

        # Algoritmo de suma ponderada (Módulo 10 alternado)
        even_sum = 0
        odd_sum = 0

        for i, digit_str in enumerate(digits):
            digit = int(digit_str)
            if (i + 1) % 2 == 0:
                # Posiciones pares: se suman directamente
                even_sum += digit
            else:
                # Posiciones impares: se multiplican por 2. Si el resultado es >= 10, se suman sus dígitos
                multiplied = digit * 2
                odd_sum += (multiplied % 10) + (multiplied // 10)

        total_sum = even_sum + odd_sum
        last_digit_of_sum = total_sum % 10
        
        # El dígito de control esperado es el complemento a 10 del último dígito de la suma
        expected_control_num = (10 - last_digit_of_sum) % 10
        expected_control_letter = cls.CIF_LETTER_CONTROL[expected_control_num]

        # Ciertas letras de organización requieren obligatoriamente letra o número como control
        # Letras que exigen número: A, B, E, H
        # Letras que exigen letra: KPQSVW
        # El resto (CDGJNRO) acepta ambos formatos
        if organization_letter in "ABEH":
            return control_digit == str(expected_control_num)
        elif organization_letter in "KPQSVW":
            return control_digit == expected_control_letter
        else:
            return control_digit == str(expected_control_num) or control_digit == expected_control_letter

    @classmethod
    def validate_foreign_document(cls, doc: str) -> bool:
        """Validates foreign passports and identity cards.

        CWE-20: el formato NO puede ser "cualquier alfanumérico de 5-15", ya que
        eso permitiría eludir la validación de identidad con texto arbitrario.
        Se exige un patrón creíble de documento de viaje: 6-9 caracteres
        alfanuméricos, empezando por una letra (como pasaportes reales), sin
        secuencias triviales. No es una verificación de identidad real, pero sí
        impide que cualquier cadena alfanumérica corta sea aceptada como DNI.
        """
        doc = doc.strip().upper()
        if not re.match(r"^[A-Z][A-Z0-9]{5,8}$", doc):
            return False
        # Rechaza secuencias triviales (p. ej. "AAAAA1", "ABCDE1").
        if len(set(doc)) < 3:
            return False
        return True

    @classmethod
    def validate_document(cls, doc: str) -> bool:
        """Main method that automatically detects the format and validates the document."""
        if not doc:
            return False

        clean_doc = doc.strip().upper()

        # 1. Matches DNI pattern?
        if re.match(r"^\d{8}[A-Z]$", clean_doc):
            return cls.validate_dni(clean_doc)

        # 2. Matches NIE pattern?
        if re.match(r"^[XYZ]\d{7}[A-Z]$", clean_doc):
            return cls.validate_nie(clean_doc)

        # 3. Matches CIF pattern (company tax id)?
        if re.match(r"^[ABCDEFGHJNPQRSTUVWXY]\d{7}[A-J0-9]$", clean_doc):
            return cls.validate_cif(clean_doc)

        # 4. Otherwise, treat it as a foreign passport/ID with strict format.
        return cls.validate_foreign_document(clean_doc)
