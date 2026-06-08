import { Routes } from '@angular/router';
import { History } from './history/history';
import { Profile } from './profile/profile';
import { BookingDetail } from './booking-detail/booking-detail';

export const CLIENT_ROUTES: Routes = [
  {
    path: '',
    redirectTo: 'history', // Al entrar a /client, redirige a /client/history
    pathMatch: 'full'
  },
  {
    path: 'history', // URL: /client/history
    component: History,
    title: 'Mis Reservas'
  },
  {
    path: 'profile', // URL: /client/profile
    component: Profile,
    title: 'Mis Datos'
  },
  {
    path: 'booking/:id', // Ruta para el detalle
    component: BookingDetail,
    title: 'Detalle de Reserva'
  }
];