import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Auth } from '../../../core/services/auth';
import { finalize, timeout, TimeoutError } from 'rxjs';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-login-admin',
  imports: [CommonModule, ReactiveFormsModule, TranslateModule],
  templateUrl: './login-admin.html',
  styleUrl: './login-admin.scss',
})
export class LoginAdmin {

  private fb = inject(FormBuilder);
  private authService = inject(Auth);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  errorMessage: string = '';
  isLoading: boolean = false;

  loginForm: FormGroup = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required]]
  });

  returnUrl: string = '/'; 

  ngOnInit(): void {
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/admin/dashboard';
  }

  isFieldInvalid(fieldName: string): boolean {
    const field = this.loginForm.get(fieldName);
    return !!(field && field.invalid && (field.dirty || field.touched));
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

    this.authService.loginAdmin(credentials)
      .pipe(
        timeout(5000),
        finalize(() => {
          this.isLoading = false;
          this.loginForm.enable();
        })
      ).subscribe({
      next: (response) => {
        console.log('Login Admin exitoso:', response);
        this.router.navigateByUrl(this.returnUrl);
      },
      error: (err) => {
        console.error('Error en login Admin:', err);
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
