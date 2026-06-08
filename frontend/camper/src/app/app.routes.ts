import { Routes } from '@angular/router';

export const routes: Routes = [
  // RUTA POR DEFECTO (Home)
  // Cuando la URL está vacía (''), carga el módulo Public.
  // Como en public.routes.ts dijimos que '' es SearchParking, 
  // esto mostrará el buscador al entrar a la web.
  {
    path: '',
    loadChildren: () => import('./features/public/public.routes').then(m => m.PUBLIC_ROUTES)
  },

  // RUTAS DE AUTENTICACIÓN
  // Cuando la URL empieza por 'auth', carga el módulo Auth.
  {
    path: 'auth',
    loadChildren: () => import('./features/auth/auth.routes').then(m => m.AUTH_ROUTES)
  },

  // RUTAS DE CLIENTE
  // Cuando la URL empieza por 'client', carga el módulo Client.
  {
    path: 'client',
    loadChildren: () => import('./features/client/client.routes').then(m => m.CLIENT_ROUTES)
  },

  // RUTAS DE ADMIN 
  // Cuando la URL empieza por 'admin', carga el módulo Admin.
  {
    path: 'admin',
    loadChildren: () => import('./features/admin/admin.routes').then(m => m.ADMIN_ROUTES)
  },

  // Si no se encuentra la ruta, redirige al home.
  { path: '**', redirectTo: '' }
];