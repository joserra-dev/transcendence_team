import { Routes } from '@angular/router';
import { Dashboard } from './dashboard/dashboard';
import { ManageParking } from './manage-parking/manage-parking';
import { ManageUsers } from './manage-users/manage-users';
import { ManageCompanies } from './manage-companies/manage-companies';
import { ManageCompanyDetail } from './manage-company-detail/manage-company-detail';
import { CompanyParkings } from './company-parkings/company-parkings';
import { ManageBookings } from './manage-bookings/manage-bookings';
import { adminGuard, adminOnlyGuard, superAdminGuard } from '../../core/guards/admin.guard';

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
    canActivate: [adminOnlyGuard],
    data: { breadcrumb: 'BREADCRUMB.DASHBOARD' },
  },
  {
    path: 'companies',
    component: ManageCompanies,
    title: 'Gestionar empresas',
    canActivate: [superAdminGuard],
    data: { breadcrumb: 'BREADCRUMB.MANAGE_COMPANIES' },
  },
  {
    path: 'companies/:id/parkings',
    component: CompanyParkings,
    title: 'Parkings de empresa',
    canActivate: [superAdminGuard],
    data: { breadcrumb: 'BREADCRUMB.COMPANY_PARKINGS' },
  },
  {
    path: 'companies/:id/edit',
    component: ManageCompanyDetail,
    title: 'Editar empresa',
    canActivate: [superAdminGuard],
    data: { breadcrumb: 'BREADCRUMB.EDIT_COMPANY' },
  },
  {
    path: 'users',
    component: ManageUsers,
    title: 'Gestionar usuarios',
    canActivate: [superAdminGuard],
    data: { breadcrumb: 'BREADCRUMB.MANAGE_USERS' },
  },
  {
    path: 'bookings',
    component: ManageBookings,
    title: 'Gestionar reservas',
    canActivate: [adminOnlyGuard],
    data: { breadcrumb: 'BREADCRUMB.MANAGE_BOOKINGS' },
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
