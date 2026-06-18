import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';

import { User, AdminUser, Company } from '../models/user';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: User;
}

export interface RegisterRequest {
  email: string;
  password: string;
  confirmPassword: string;
}

export interface ResetPasswordRequest {
  token: string;
  password: string;
  confirmPassword: string;
}

export interface RegisterResponse {
  mensaje: string;
  usuario: { id: number; email: string };
}

@Injectable({
  providedIn: 'root'
})
export class Auth {
  private http = inject(HttpClient);
  private router = inject(Router);

  private apiUrl = `${window.env.URL_BACK}/api/users`;

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(
      `${this.apiUrl}/login`,
      credentials
    ).pipe(
      tap(response => this.saveSession(response))
    );
  }

  register(data: RegisterRequest): Observable<RegisterResponse> {
    return this.http.post<RegisterResponse>(
      `${this.apiUrl}/register`,
      data
    );
  }

  requestPasswordReset(email: string): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.apiUrl}/forgot-password`, { email });
  }

  resetPassword(data: ResetPasswordRequest): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.apiUrl}/reset-password`, data);
  }

  loginAdmin(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(
      `${this.apiUrl}/admin-login`,
      credentials
    ).pipe(
      tap(response => this.saveSession(response))
    );
  }

  private saveSession(data: LoginResponse): void {
    sessionStorage.setItem('token', data.token);
    sessionStorage.setItem('user', JSON.stringify(data.user));
  }

  logout(): void {
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user');
    this.router.navigate(['/auth/login-client']);
  }

  isLoggedIn(): boolean {
    const token = sessionStorage.getItem('token');
    if (!token) return false;

    try {
      // Decodifica la parte del payload del JWT (índice 1) sin librería externa
      const payload = JSON.parse(atob(token.split('.')[1]));
      const now = Math.floor(Date.now() / 1000);

      if (payload.exp && payload.exp < now) {
        // Token expirado → limpiar sessionStorage
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('user');
        return false;
      }
      return true;
    } catch {
      // Token malformado → limpiar por seguridad
      sessionStorage.removeItem('token');
      sessionStorage.removeItem('user');
      return false;
    }
  }

  getUser(): User | null {
    const userStr = sessionStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  isAdmin(): boolean {
    const role = this.getUser()?.role;
    return role === 'admin' || role === 'super_admin' || this.getUser()?.admin === true;
  }

  isSuperAdmin(): boolean {
    return this.getUser()?.role === 'super_admin';
  }

  logoutAdmin(): void {
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user');
    this.router.navigate(['/auth/login-admin']);
  }
}