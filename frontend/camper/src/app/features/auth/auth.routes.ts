import { Routes } from '@angular/router';
import { Login } from './login/login';
import { Register } from './register/register';
import { LoginAdmin } from './login-admin/login-admin';

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
  { path: '', redirectTo: 'login-client', pathMatch: 'full' }
];