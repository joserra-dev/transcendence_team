import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

export class CustomValidators {

  // 1. Validar Mayoría de Edad
  static mayorDeEdad(control: AbstractControl): ValidationErrors | null {
    if (!control.value) return null;

    const fechaNacimiento = new Date(control.value);
    const hoy = new Date();
    const edad = hoy.getFullYear() - fechaNacimiento.getFullYear();
    const mes = hoy.getMonth() - fechaNacimiento.getMonth();

    if (mes < 0 || (mes === 0 && hoy.getDate() < fechaNacimiento.getDate())) {
      if (edad - 1 < 18) return { menorDeEdad: true };
    } else {
      if (edad < 18) return { menorDeEdad: true };
    }
    return null;
  }

  // 2. Validar DNI Español
  static dniValido(control: AbstractControl): ValidationErrors | null {
    const dni = control.value;
    if (!dni) return null;

    const regex = /^[0-9]{8}[A-Za-z]$/;
    if (!regex.test(dni)) return { dniFormato: true };

    const letras = 'TRWAGMYFPDXBNJZSQVHLCKE';
    const numero = parseInt(dni.substring(0, 8), 10);
    const letraCalculada = letras.charAt(numero % 23);
    const letraEntrada = dni.substring(8).toUpperCase();

    return letraCalculada === letraEntrada ? null : { dniInvalido: true };
  }

  // 2b. Validar CIF Español (misma lógica que el backend IdentityValidator)
  static cifValido(control: AbstractControl): ValidationErrors | null {
    const value = control.value;
    if (!value) return null;

    const cif = String(value).trim().toUpperCase();
    const regex = /^[ABCDEFGHJNPQRSTUVWXY]\d{7}[A-J0-9]$/;
    if (!regex.test(cif)) return { cifInvalido: true };

    const organizationLetter = cif.charAt(0);
    const digits = cif.substring(1, 8);
    const controlDigit = cif.charAt(8);

    let evenSum = 0;
    let oddSum = 0;
    for (let i = 0; i < digits.length; i++) {
      const digit = parseInt(digits.charAt(i), 10);
      if ((i + 1) % 2 === 0) {
        evenSum += digit;
      } else {
        const multiplied = digit * 2;
        oddSum += (multiplied % 10) + Math.floor(multiplied / 10);
      }
    }

    const lastDigitOfSum = (evenSum + oddSum) % 10;
    const expectedControlNum = (10 - lastDigitOfSum) % 10;
    const controlLetters = 'JABCDEFGHI';
    const expectedControlLetter = controlLetters.charAt(expectedControlNum);

    let isValid: boolean;
    if ('ABEH'.includes(organizationLetter)) {
      isValid = controlDigit === String(expectedControlNum);
    } else if ('KPQSVW'.includes(organizationLetter)) {
      isValid = controlDigit === expectedControlLetter;
    } else {
      isValid =
        controlDigit === String(expectedControlNum) || controlDigit === expectedControlLetter;
    }

    return isValid ? null : { cifInvalido: true };
  }

  // 3. Comparar Contraseñas (Password y ConfirmPassword)
  // Solo valida si al menos uno de los campos tiene valor; si ambos están vacíos, es válido
  // (el usuario no quiere cambiar la contraseña)
  static matchPasswords(passwordKey: string, confirmPasswordKey: string): ValidatorFn {
    return (group: AbstractControl): ValidationErrors | null => {
      const password = group.get(passwordKey)?.value ?? '';
      const confirmPassword = group.get(confirmPasswordKey)?.value ?? '';

      // Si ambos están vacíos, no hay nada que validar
      if (!password && !confirmPassword) return null;

      return password === confirmPassword ? null : { passwordsMismatch: true };
    };
  }

  // 4. Validar contraseña (misma lógica que backend PasswordValidator)
  static passwordStrength(emailField: string = 'email'): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      const password = control.value;
      if (!password) return null;

      const passwordLower = String(password).toLowerCase();
      const email = control.parent?.get(emailField)?.value ?? '';

      if (passwordLower.includes('password')) {
        return { passwordForbiddenWord: true };
      }

      if (email && String(email).includes('@')) {
        const emailUsername = String(email).split('@')[0].toLowerCase();
        if (emailUsername && passwordLower.includes(emailUsername)) {
          return { passwordContainsEmail: true };
        }
      }

      if (!/[A-Z]/.test(password)) return { passwordUppercase: true };
      if (!/[a-z]/.test(password)) return { passwordLowercase: true };
      if (!/\d/.test(password)) return { passwordDigit: true };
      if (!/[@$!%*?&]/.test(password)) return { passwordSpecialChar: true };

      const regex = /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
      if (!regex.test(password)) return { passwordInvalidFormat: true };

      return null;
    };
  }

  // 5. Validar IBAN (Formato ES + 22 dígitos)
  /*static ibanValido(control: AbstractControl): ValidationErrors | null {
    const iban = control.value;
    const regex = /^ES\d{22}$/;
    if (iban && !regex.test(iban)) {
      return { ibanInvalido: true };
    }
    return null;
  }*/
}
