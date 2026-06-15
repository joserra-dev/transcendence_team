import { Routes } from '@angular/router';
import { Dashboard } from './dashboard/dashboard';
import { ManageParking } from './manage-parking/manage-parking';
import { adminGuard } from '../../core/guards/admin.guard';

export const ADMIN_ROUTES: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full'
  },
  {
    path: 'dashboard',
    component: Dashboard,
    title: 'Admin Dashboard',
    canActivate: [adminGuard]
  },
  {
    path: 'parking/new',
    component: ManageParking,
    title: 'Nuevo Parking',
    canActivate: [adminGuard]
  },
  {
    path: 'parking/:id',
    component: ManageParking,
    title: 'Gestionar Parking',
    canActivate: [adminGuard]
  }
];