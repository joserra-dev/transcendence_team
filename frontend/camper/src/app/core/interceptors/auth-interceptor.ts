import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { Auth } from '../services/auth';

/**
 * Interceptor HTTP que:
 * 1. Añade el token Bearer a todas las peticiones autenticadas.
 * 2. Captura respuestas 401 (token expirado o inválido) y hace logout automático,
 *    resolviendo el problema de inactividad donde el token expira pero la UI
 *    sigue mostrando al usuario como logueado.
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(Auth);

  // Rutas públicas: no necesitan token
  if (req.url.includes('/auth/') || req.url.includes('/api/public/')) {
    return next(req);
  }

  const token = sessionStorage.getItem('token');

  const authReq = token
    ? req.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
    : req;

  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        // Token expirado o inválido → limpiar sesión y redirigir al login
        authService.logout();
      }
      return throwError(() => error);
    })
  );
};