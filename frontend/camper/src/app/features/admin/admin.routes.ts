import { Routes } from '@angular/router';
import { Dashboard } from './dashboard/dashboard';
import { ManageParking } from './manage-parking/manage-parking';
import { ManageUsers } from './manage-users/manage-users';
import { adminGuard, superAdminGuard } from '../../core/guards/admin.guard';

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
    canActivate: [adminGuard],
    data: { breadcrumb: 'BREADCRUMB.DASHBOARD' },
  },
  {
    path: 'users',
    component: ManageUsers,
    title: 'Gestionar usuarios',
    canActivate: [superAdminGuard],
    data: { breadcrumb: 'BREADCRUMB.MANAGE_USERS' },
  },
  {
    path: 'parking/new',
    component: ManageParking,
    title: 'Nuevo Parking',
    canActivate: [adminGuard],
    data: {
      breadcrumbs: [
        { labelKey: 'BREADCRUMB.HOME', url: '/' },
        { labelKey: 'BREADCRUMB.DASHBOARD', url: '/admin/dashboard' },
        { labelKey: 'BREADCRUMB.NEW_PARKING' },
      ],
    },
  },
  {
    path: 'parking/:id',
    component: ManageParking,
    title: 'Gestionar Parking',
    canActivate: [adminGuard],
    data: {
      breadcrumbs: [
        { labelKey: 'BREADCRUMB.HOME', url: '/' },
        { labelKey: 'BREADCRUMB.DASHBOARD', url: '/admin/dashboard' },
        { labelKey: 'BREADCRUMB.MANAGE_PARKING' },
      ],
    },
  }
];
