import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';

import { User } from '../models/user';

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

// Estructura interna del Payload del JWT
interface JwtPayload {
  sub?: string;
  role?: string;
  admin?: boolean;
  exp?: number;
  [key: string]: unknown;
}

@Injectable({
  providedIn: 'root'
})
export class Auth {
  private http = inject(HttpClient);
  private router = inject(Router);

  private apiUrl = `${(window.env?.URL_BACK || 'http://localhost:5000').replace(/\/$/, '')}/api/users`;

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

  /**
   * Decodifica el payload del JWT de forma segura sin librerías externas
   */
  private getPayloadFromToken(): JwtPayload | null {
    const token = sessionStorage.getItem('token');
    if (!token) return null;

    try {
      const parts = token.split('.');
      if (parts.length !== 3) return null;

      // Decodificación base64url compatible con UTF-8
      const base64Url = parts[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );

      return JSON.parse(jsonPayload) as JwtPayload;
    } catch {
      return null;
    }
  }

  isLoggedIn(): boolean {
    const payload = this.getPayloadFromToken();
    if (!payload) return false;

    const now = Math.floor(Date.now() / 1000);
    if (payload.exp && payload.exp < now) {
      sessionStorage.removeItem('token');
      sessionStorage.removeItem('user');
      return false;
    }
    return true;
  }

  /**
   * Devuelve los datos estéticos/visuales del usuario (ej: nombre para el navbar).
   */
  getUser(): User | null {
    const userStr = sessionStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  /**
   * Verifica los permisos leyendo ÚNICAMENTE el token JWT firmado
   */
  isAdmin(): boolean {
    if (!this.isLoggedIn()) return false;

    const payload = this.getPayloadFromToken();
    if (!payload) return false;

    const role = payload.role;
    return role === 'admin' || role === 'super_admin' || payload.admin === true;
  }

  /**
   * Verifica permisos de Super Admin usando ÚNICAMENTE el token JWT
   */
  isSuperAdmin(): boolean {
    if (!this.isLoggedIn()) return false;

    const payload = this.getPayloadFromToken();
    return payload?.role === 'super_admin';
  }

  logoutAdmin(): void {
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user');
    this.router.navigate(['/auth/login-admin']);
  }
}