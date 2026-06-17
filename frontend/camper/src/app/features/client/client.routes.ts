import { Routes } from '@angular/router';
import { History } from './history/history';
import { Profile } from './profile/profile';
import { BookingDetail } from './booking-detail/booking-detail';
import { authGuard } from '../../core/guards/auth.guard';

export const CLIENT_ROUTES: Routes = [
  {
    path: '',
    redirectTo: 'history', // Al entrar a /client, redirige a /client/history
    pathMatch: 'full'
  },
  {
    path: 'history', // URL: /client/history
    component: History,
    title: 'Mis Reservas',
    canActivate: [authGuard],
    data: { breadcrumb: 'BREADCRUMB.HISTORY' },
  },
  {
    path: 'profile', // URL: /client/profile
    component: Profile,
    title: 'Mis Datos',
    canActivate: [authGuard],
    data: { breadcrumb: 'BREADCRUMB.PROFILE' },
  },
  {
    path: 'booking/:id', // Ruta para el detalle
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
  }
];