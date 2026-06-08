import { Routes } from '@angular/router';
import { Dashboard } from './dashboard/dashboard';
import { ManageParking } from './manage-parking/manage-parking';

export const ADMIN_ROUTES: Routes = [
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full'
  },
  {
    path: 'dashboard',
    component: Dashboard,
    title: 'Admin Dashboard'
  },
  {
    path: 'parking/new',
    component: ManageParking, 
    title: 'Nuevo Parking'
  },
  {
    path: 'parking/:id',
    component: ManageParking,
    title: 'Gestionar Parking'
  }
];