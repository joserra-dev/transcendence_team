import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { Auth } from '../services/auth';

/**
 * Guard que protege las rutas exclusivas de administrador.
 * Si el usuario no es admin (o no tiene sesión), lo redirige al home.
 */
export const adminGuard: CanActivateFn = (_route, _state) => {
  const authService = inject(Auth);
  const router = inject(Router);

  if (authService.isLoggedIn() && authService.isAdmin()) {
    return true;
  }

  // Si está logueado pero no es admin → redirige al home
  if (authService.isLoggedIn()) {
    return router.createUrlTree(['/']);
  }

  // Si no tiene sesión → redirige al login
  return router.createUrlTree(['/auth/login-client']);
};
