import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Auth, RegisterRequest } from '../../../core/services/auth';
import { CustomValidators } from '../../../shared/validators/custom-validators/custom-validators';
import { finalize, timeout, TimeoutError } from 'rxjs';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-register',
  imports: [CommonModule, ReactiveFormsModule, RouterLink, TranslateModule],
  templateUrl: './register.html',
  styleUrl: './register.scss',
})
export class Register {
  private fb = inject(FormBuilder);
  private authService = inject(Auth);
  private router = inject(Router);

  apiErrors: string[] = [];
  successMessage: string = '';
  isLoading = false;

  registerForm: FormGroup = this.fb.group({
    //nombre: ['', Validators.required],
    //apellidos: ['', Validators.required],
    //dni: ['', [Validators.required, CustomValidators.dniValido]],
    //fechaNacimiento: ['', [Validators.required, CustomValidators.mayorDeEdad]],
    //iban: ['', [Validators.required, CustomValidators.ibanValido]],
    email: ['', [Validators.required, Validators.email]],
    password: ['', Validators.required],
    confirmPassword: ['', Validators.required]
  }, {
    validators: CustomValidators.matchPasswords('password', 'confirmPassword')
  });

  isInvalid(field: string): boolean {
    const control = this.registerForm.get(field);
    return !!(control && control.invalid && (control.dirty || control.touched));
  }

  onSubmit() {
    if (this.registerForm.invalid) {
      this.registerForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    this.registerForm.disable();
    this.apiErrors = [];
    this.successMessage = '';

    const formValue = this.registerForm.value;
    const requestData: RegisterRequest = {
      //nombrePersona: formValue.nombre,
      //apellidosPersona: formValue.apellidos,
      //fecNacimientoPersona: formValue.fechaNacimiento,
      //dniPersona: formValue.dni,
      //ibanPersona: formValue.iban,
      email: formValue.email,
      password: formValue.password,
      confirmPassword: formValue.confirmPassword
      //admin: false
    };

    this.authService.register(requestData).pipe(
      timeout(5000),
        finalize(() => {
          this.isLoading = false;
          this.registerForm.enable();
        })
      ).subscribe({
      next: (response) => {
        this.successMessage = response;
        this.isLoading = false;
        this.registerForm.reset();

        setTimeout(() => {
          this.router.navigate(['/auth/login-client']);
        }, 3000);
      },
      error: (err) => {
        console.error('Error registro:', err);

        if (err instanceof TimeoutError) {
             this.apiErrors = ['REGISTER.BACKEND.TIMEOUT'];
          }
        else if (err.status === 409) {
          this.apiErrors = [err.error || 'REGISTER.BACKEND.USER_EXISTS'];
        }

        else if (err.status === 400) {
          if (typeof err.error === 'string') {
             try {
                const parsedError = JSON.parse(err.error);
                this.apiErrors = Array.isArray(parsedError) ? parsedError : [parsedError];
             } catch (e) {
                this.apiErrors = [err.error];
             }
          } else if (Array.isArray(err.error)) {
             this.apiErrors = err.error;
          }
        }

        else {
          this.apiErrors = ['REGISTER.BACKEND.UNKNOWN'];
        }
      }
    });
  }
}
