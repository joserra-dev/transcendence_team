import { Routes } from '@angular/router';
import { SearchParking } from './search-parking/search-parking';
import { ParkingDetail } from './parking-detail/parking-detail';

export const PUBLIC_ROUTES: Routes = [
  {
    path: '',
    component: SearchParking,
    title: 'Buscar Parking'
  },
  { path: 'parking/:id', 
    component: ParkingDetail,
    title: 'Detalles Parking' }
];