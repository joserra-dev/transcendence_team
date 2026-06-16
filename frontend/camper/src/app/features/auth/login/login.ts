import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Auth } from '../../../core/services/auth';
import { finalize, timeout, TimeoutError } from 'rxjs';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-login',
  imports: [CommonModule, ReactiveFormsModule, TranslateModule],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})

export class Login {
  private fb = inject(FormBuilder);
  private authService = inject(Auth);
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  hidePassword = true;
  errorMessage: string = '';
  isLoading: boolean = false;
  isRecoveryLoading: boolean = false;
  recoveryMessage: string = '';
  recoveryMessageType: 'success' | 'error' | '' = '';
  showRecoveryModal: boolean = false;

  loginForm: FormGroup = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required]]
  });

  recoveryForm: FormGroup = this.fb.group({
    email: ['', [Validators.required, Validators.email]]
  });

  returnUrl: string = '/'; 

  ngOnInit(): void {
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/public';
  }

  isFieldInvalid(fieldName: string): boolean {
    const field = this.loginForm.get(fieldName);
    return !!(field && field.invalid && (field.dirty || field.touched));
  }

  isRecoveryFieldInvalid(fieldName: string): boolean {
    const field = this.recoveryForm.get(fieldName);
    return !!(field && field.invalid && (field.dirty || field.touched));
  }

  openRecoveryModal(): void {
    this.recoveryMessage = '';
    this.recoveryMessageType = '';
    this.showRecoveryModal = true;
  }

  closeRecoveryModal(): void {
    this.showRecoveryModal = false;
    this.recoveryMessage = '';
    this.recoveryMessageType = '';
    this.recoveryForm.reset();
  }

  sendRecoveryEmail(): void {
    if (this.recoveryForm.invalid) {
      this.recoveryForm.markAllAsTouched();
      return;
    }

    this.isRecoveryLoading = true;
    this.recoveryMessage = '';
    this.recoveryMessageType = '';
    const { email } = this.recoveryForm.value;

    this.authService.requestPasswordReset(email).pipe(
      timeout(5000),
      finalize(() => {
        this.isRecoveryLoading = false;
      })
    ).subscribe({
      next: () => {
        this.recoveryMessage = 'LOGIN.RECOVERY.SUCCESS';
        this.recoveryMessageType = 'success';
        this.recoveryForm.reset();
      },
      error: (err) => {
        console.error('Error solicitando recuperación:', err);
        if (err instanceof TimeoutError) {
          this.recoveryMessage = 'LOGIN.RECOVERY.ERROR.TIMEOUT';
        } else {
          this.recoveryMessage = 'LOGIN.RECOVERY.ERROR.UNKNOWN';
        }
        this.recoveryMessageType = 'error';
      }
    });
  }

  onSubmit() {
    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      return;
    }

    this.errorMessage = '';
    this.isLoading = true;
    this.loginForm.disable();

    const credentials = this.loginForm.value;

    this.authService.login(credentials)
      .pipe(
        timeout(5000),
        finalize(() => {
          this.isLoading = false;
          this.loginForm.enable();
        })
      ).subscribe({
      next: (response) => {
        this.router.navigateByUrl(this.returnUrl);
      },
      error: (err) => {
        if (err instanceof TimeoutError) {
             this.errorMessage = 'LOGIN.ERROR.TIMEOUT';
        } else if (err.status === 401 || err.status === 404) {
          this.errorMessage = 'LOGIN.ERROR.INVALID_CREDENTIALS';
        } else {
          this.errorMessage = 'LOGIN.ERROR.UNKNOWN';
        }
      }
    });
  }
}
