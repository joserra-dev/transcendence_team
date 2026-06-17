import { Routes } from '@angular/router';
import { Login } from './login/login';
import { Register } from './register/register';
import { LoginAdmin } from './login-admin/login-admin';
import { ResetPassword } from './reset-password/reset-password';

export const AUTH_ROUTES: Routes = [
  {
    path: 'login-client',
    component: Login,
    data: { breadcrumb: 'BREADCRUMB.LOGIN' },
  },
  {
    path: 'login-admin',
    component: LoginAdmin,
    title: 'Login Administrador',
    data: { breadcrumb: 'BREADCRUMB.LOGIN_ADMIN' },
  },
  {
    path: 'register',
    component: Register,
    data: { breadcrumb: 'BREADCRUMB.REGISTER' },
  },
  {
    path: 'reset-password',
    component: ResetPassword,
    title: 'Restablecer contraseña',
    data: { breadcrumb: 'BREADCRUMB.RESET_PASSWORD' },
  },
  { path: '', redirectTo: 'login-client', pathMatch: 'full' }
];