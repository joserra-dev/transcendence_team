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

  private extractBackendErrors(err: { error?: unknown; status?: number }): string[] {
    const body = err?.error;
    if (!body) {
      return ['REGISTER.BACKEND.UNKNOWN'];
    }
    if (typeof body === 'string') {
      try {
        const parsed = JSON.parse(body) as { error?: string } | string;
        if (typeof parsed === 'string') {
          return [parsed];
        }
        if (parsed.error) {
          return [parsed.error];
        }
      } catch {
        return [body];
      }
    }
    if (typeof body === 'object' && body !== null && 'error' in body && typeof (body as { error: unknown }).error === 'string') {
      return [(body as { error: string }).error];
    }
    if (Array.isArray(body)) {
      return body.map((item) => (typeof item === 'string' ? item : 'REGISTER.BACKEND.UNKNOWN'));
    }
    return ['REGISTER.BACKEND.UNKNOWN'];
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
      next: () => {
        this.successMessage = 'REGISTER.SUCCESS';
        this.registerForm.reset();

        setTimeout(() => {
          this.router.navigate(['/auth/login-client']);
        }, 3000);
      },
      error: (err) => {
        if (err instanceof TimeoutError) {
          this.apiErrors = ['REGISTER.BACKEND.TIMEOUT'];
        } else if (err.status === 409) {
          this.apiErrors = ['REGISTER.BACKEND.USER_EXISTS'];
        } else if (err.status === 400) {
          this.apiErrors = this.extractBackendErrors(err);
        } else {
          this.apiErrors = ['REGISTER.BACKEND.UNKNOWN'];
        }
      }
    });
  }
}
