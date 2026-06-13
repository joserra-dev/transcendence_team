import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize, timeout, TimeoutError } from 'rxjs';
import { TranslateModule } from '@ngx-translate/core';
import { Auth } from '../../../core/services/auth';

@Component({
  selector: 'app-reset-password',
  imports: [CommonModule, ReactiveFormsModule, RouterLink, TranslateModule],
  templateUrl: './reset-password.html',
  styleUrl: './reset-password.scss'
})
export class ResetPassword {
  private fb = inject(FormBuilder);
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private authService = inject(Auth);

  token = '';
  isLoading = false;
  errorMessage = '';
  successMessage = '';

  resetForm = this.fb.group({
    password: ['', [Validators.required, Validators.minLength(8)]],
    confirmPassword: ['', [Validators.required]]
  });

  ngOnInit(): void {
    this.token = this.route.snapshot.queryParamMap.get('token') ?? '';
    if (!this.token) {
      this.errorMessage = 'RESET_PASSWORD.ERRORS.TOKEN_MISSING';
    }
  }

  isFieldInvalid(fieldName: string): boolean {
    const field = this.resetForm.get(fieldName);
    return !!(field && field.invalid && (field.dirty || field.touched));
  }

  submit(): void {
    if (!this.token) {
      this.errorMessage = 'RESET_PASSWORD.ERRORS.TOKEN_MISSING';
      return;
    }

    if (this.resetForm.invalid) {
      this.resetForm.markAllAsTouched();
      return;
    }

    const { password, confirmPassword } = this.resetForm.value;
    this.isLoading = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.authService.resetPassword({
      token: this.token,
      password: password ?? '',
      confirmPassword: confirmPassword ?? ''
    }).pipe(
      timeout(5000),
      finalize(() => {
        this.isLoading = false;
      })
    ).subscribe({
      next: () => {
        this.successMessage = 'RESET_PASSWORD.SUCCESS';
        setTimeout(() => {
          this.router.navigate(['/auth/login-client']);
        }, 2000);
      },
      error: (err) => {
        console.error('Error restableciendo contraseña:', err);
        if (err instanceof TimeoutError) {
          this.errorMessage = 'RESET_PASSWORD.ERRORS.TIMEOUT';
        } else if (err.status === 400) {
          this.errorMessage = err.error?.error || 'RESET_PASSWORD.ERRORS.INVALID_TOKEN';
        } else {
          this.errorMessage = 'RESET_PASSWORD.ERRORS.UNKNOWN';
        }
      }
    });
  }
}
