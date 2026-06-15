import { Routes } from '@angular/router';
import { Login } from './login/login';
import { Register } from './register/register';
import { LoginAdmin } from './login-admin/login-admin';
import { ResetPassword } from './reset-password/reset-password';

export const AUTH_ROUTES: Routes = [
  {
    path: 'login-client', 
    component: Login
  },
  {
    path: 'login-admin',
    component: LoginAdmin,
    title: 'Login Administrador'
  },
  {
    path: 'register',    
    component: Register
  },
  {
    path: 'reset-password',
    component: ResetPassword,
    title: 'Restablecer contraseña'
  },
  { path: '', redirectTo: 'login-client', pathMatch: 'full' }
];