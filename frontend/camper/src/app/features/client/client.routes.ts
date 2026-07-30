import { Routes } from '@angular/router';
import { History } from './history/history';
import { Profile } from './profile/profile';
import { BookingDetail } from './booking-detail/booking-detail';
import { BookingCancelled } from './booking-cancelled/booking-cancelled';
import { authGuard } from '../../core/guards/auth.guard';

export const CLIENT_ROUTES: Routes = [
  {
    path: '',
    redirectTo: 'history',
    pathMatch: 'full'
  },
  {
    path: 'history',
    component: History,
    title: 'Mis Reservas',
    canActivate: [authGuard],
    data: { breadcrumb: 'BREADCRUMB.HISTORY' },
  },
  {
    path: 'profile',
    component: Profile,
    title: 'Mis Datos',
    canActivate: [authGuard],
    data: { breadcrumb: 'BREADCRUMB.PROFILE' },
  },
  {
    path: 'booking/:id',
    component: BookingDetail,
    title: 'Detalle de Reserva',
    canActivate: [authGuard],
    data: {
      breadcrumbs: [
        { labelKey: 'BREADCRUMB.HOME', url: '/' },
        { labelKey: 'BREADCRUMB.HISTORY', url: '/client/history' },
        { labelKey: 'BREADCRUMB.BOOKING_DETAIL' },
      ],
    },
  },
  {
    path: 'booking/cancelled/:id',
    component: BookingCancelled,
    title: 'Reserva',
    canActivate: [authGuard],
    data: {
      breadcrumbs: [
        { labelKey: 'BREADCRUMB.HOME', url: '/' },
        { labelKey: 'BREADCRUMB.HISTORY', url: '/client/history' },
      ],
    },
  }
];