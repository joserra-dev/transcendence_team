import { Routes } from '@angular/router';
import { Dashboard } from './dashboard/dashboard';
import { ManageParking } from './manage-parking/manage-parking';
import { ManageUsers } from './manage-users/manage-users';
import { ManageCompanies } from './manage-companies/manage-companies';
import { ManageCompanyDetail } from './manage-company-detail/manage-company-detail';
import { CompanyParkings } from './company-parkings/company-parkings';
import { CompanyMetricsPage } from './company-metrics/company-metrics';
import { ManageBookings } from './manage-bookings/manage-bookings';
import { Calendar } from './calendar/calendar';
import { AdminChat } from './admin-chat/admin-chat';
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
    path: 'companies/:id/metrics',
    component: CompanyMetricsPage,
    title: 'Métricas de empresa',
    canActivate: [superAdminGuard],
    data: { breadcrumb: 'BREADCRUMB.COMPANY_METRICS' },
  },
  {
    path: 'metrics',
    component: CompanyMetricsPage,
    title: 'Métricas',
    canActivate: [adminOnlyGuard],
    data: { breadcrumb: 'BREADCRUMB.METRICS' },
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
    path: 'calendar',
    component: Calendar,
    title: 'Calendarios',
    canActivate: [adminOnlyGuard],
    data: { breadcrumb: 'BREADCRUMB.CALENDAR' },
  },
  {
    path: 'chat',
    component: AdminChat,
    title: 'Chat de incidencias',
    canActivate: [adminGuard],
    data: { breadcrumb: 'BREADCRUMB.ADMIN_CHAT' },
  },
  {
    path: 'parking/new',
    component: ManageParking,
    title: 'Nuevo Parking',
    canActivate: [adminGuard],
    data: {
      breadcrumbs: [
        { labelKey: 'BREADCRUMB.HOME', url: '/admin/dashboard' },
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
        { labelKey: 'BREADCRUMB.HOME', url: '/admin/dashboard' },
        { labelKey: 'BREADCRUMB.DASHBOARD', url: '/admin/dashboard' },
        { labelKey: 'BREADCRUMB.MANAGE_PARKING' },
      ],
    },
  }
];
