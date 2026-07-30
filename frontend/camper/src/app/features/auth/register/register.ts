import { Component, DestroyRef, inject, OnInit } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
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
export class Register implements OnInit {
  private fb = inject(FormBuilder);
  private authService = inject(Auth);
  private router = inject(Router);
  private destroyRef = inject(DestroyRef);

  apiErrors: string[] = [];
  successMessage: string = '';
  isLoading = false;

  readonly passwordRules: Array<{
    key: string;
    label: string;
    test: (password: string, email: string) => boolean;
  }> = [
    {
      key: 'minLength',
      label: 'REGISTER.PASSWORD_RULES.MIN_LENGTH',
      test: (password) => password.length >= 8,
    },
    {
      key: 'uppercase',
      label: 'REGISTER.PASSWORD_RULES.UPPERCASE',
      test: (password) => /[A-Z]/.test(password),
    },
    {
      key: 'lowercase',
      label: 'REGISTER.PASSWORD_RULES.LOWERCASE',
      test: (password) => /[a-z]/.test(password),
    },
    {
      key: 'digit',
      label: 'REGISTER.PASSWORD_RULES.DIGIT',
      test: (password) => /\d/.test(password),
    },
    {
      key: 'specialChar',
      label: 'REGISTER.PASSWORD_RULES.SPECIAL_CHAR',
      test: (password) => /[@$!%*?&]/.test(password),
    },
    {
      key: 'forbiddenWord',
      label: 'REGISTER.PASSWORD_RULES.FORBIDDEN_WORD',
      test: (password) => !password.toLowerCase().includes('password'),
    },
    {
      key: 'noEmailPart',
      label: 'REGISTER.PASSWORD_RULES.CONTAINS_EMAIL',
      test: (password, email) => {
        if (!email || !email.includes('@')) return true;
        const username = email.split('@')[0].toLowerCase();
        return !username || !password.toLowerCase().includes(username);
      },
    },
  ];

  registerForm: FormGroup = this.fb.group({
    //nombre: ['', Validators.required],
    //apellidos: ['', Validators.required],
    //dni: ['', [Validators.required, CustomValidators.dniValido]],
    //fechaNacimiento: ['', [Validators.required, CustomValidators.mayorDeEdad]],
    //iban: ['', [Validators.required, CustomValidators.ibanValido]],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [
      Validators.required,
      Validators.minLength(8),
      Validators.maxLength(254),
      CustomValidators.passwordStrength()
    ]],
    confirmPassword: ['', Validators.required]
  }, {
    validators: CustomValidators.matchPasswords('password', 'confirmPassword')
  });

  ngOnInit(): void {
    this.registerForm.get('email')?.valueChanges
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => {
        this.registerForm.get('password')?.updateValueAndValidity({ emitEvent: false });
      });
  }

  isInvalid(field: string): boolean {
    const control = this.registerForm.get(field);
    return !!(control && control.invalid && (control.dirty || control.touched));
  }

  showPasswordFeedback(): boolean {
    const control = this.registerForm.get('password');
    if (!control) return false;
    const value = control.value ?? '';
    return value.length > 0 || control.touched;
  }

  isPasswordRuleMet(rule: { test: (password: string, email: string) => boolean }): boolean {
    const password = this.registerForm.get('password')?.value ?? '';
    const email = this.registerForm.get('email')?.value ?? '';
    if (!password) return false;
    return rule.test(password, email);
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

    this.apiErrors = [];
    this.successMessage = '';

    const formValue = this.registerForm.getRawValue();
    this.isLoading = true;
    this.registerForm.disable();

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
