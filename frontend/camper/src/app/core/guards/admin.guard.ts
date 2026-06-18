import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { Auth } from '../services/auth';

export const adminGuard: CanActivateFn = (_route, _state) => {
  const authService = inject(Auth);
  const router = inject(Router);

  if (authService.isLoggedIn() && authService.isAdmin()) {
    return true;
  }

  if (authService.isLoggedIn()) {
    return router.createUrlTree(['/public']);
  }

  return router.createUrlTree(['/auth/login-admin'], {
    queryParams: { returnUrl: _state.url },
  });
};

export const superAdminGuard: CanActivateFn = (_route, _state) => {
  const authService = inject(Auth);
  const router = inject(Router);

  if (authService.isLoggedIn() && authService.isSuperAdmin()) {
    return true;
  }

  if (authService.isLoggedIn() && authService.isAdmin()) {
    return router.createUrlTree(['/admin/dashboard']);
  }

  return router.createUrlTree(['/auth/login-admin'], {
    queryParams: { returnUrl: _state.url },
  });
};
