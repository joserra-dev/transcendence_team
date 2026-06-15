import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { Auth } from '../services/auth';

/**
 * Guard que protege las rutas que requieren autenticación.
 * Si el usuario no tiene sesión activa, lo redirige al login
 * y guarda la URL de retorno para navegar de vuelta tras el login.
 */
export const authGuard: CanActivateFn = (_route, state) => {
  const authService = inject(Auth);
  const router = inject(Router);

  if (authService.isLoggedIn()) {
    return true;
  }

  return router.createUrlTree(['/auth/login-client'], {
    queryParams: { returnUrl: state.url }
  });
};
