import { Component } from '@angular/core';
import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

@Component({
  selector: 'app-custom-validators',
  imports: [],
  templateUrl: './custom-validators.html',
  styleUrl: './custom-validators.scss',
})

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

  // 3. Comparar Contraseñas (Password y ConfirmPassword)
  static matchPasswords(passwordKey: string, confirmPasswordKey: string): ValidatorFn {
    return (group: AbstractControl): ValidationErrors | null => {
      const password = group.get(passwordKey)?.value;
      const confirmPassword = group.get(confirmPasswordKey)?.value;
      return password === confirmPassword ? null : { passwordsMismatch: true };
    };
  }

  // 4. Validar IBAN (Formato ES + 22 dígitos)
  static ibanValido(control: AbstractControl): ValidationErrors | null {
    const iban = control.value;
    const regex = /^ES\d{22}$/;
    if (iban && !regex.test(iban)) {
      return { ibanInvalido: true };
    }
    return null;
  }
}
