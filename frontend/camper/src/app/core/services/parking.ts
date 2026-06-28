import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import { Parking, SearchFilters } from '../models/parking';

@Injectable({
  providedIn: 'root'
})
export class ParkingService {
  private http = inject(HttpClient);

  private apiUrl = environment.urlBack;

  searchParkings(filters: SearchFilters): Observable<any[]> {
    let params: any = {};
    if (filters.id) {
      params.id = filters.id.toString();
    }
    if (filters.startDate) {
      params.startDate = filters.startDate;
    }
    if (filters.endDate) {
      params.endDate = filters.endDate;
    }
    if (filters.localidad) {
      params.municipio = filters.localidad;
    }
    if (filters.provincia) {
      params.provincia = filters.provincia;
    }
    if (filters.tomaElectricidad !== undefined) {
      params.electricidad = filters.tomaElectricidad.toString();
    }
    if (filters.limpiezaAguasResiduales !== undefined) {
      params.residuales = filters.limpiezaAguasResiduales.toString();
    }
    if (filters.plazasVip !== undefined) {
      params.vip = filters.plazasVip.toString();
    }
    return this.http.get<any[]>(`${this.apiUrl}/api/parking/search`, { params });
  }

  getParkingById(id: string | number): Observable<Parking> {
    return this.http.post<Parking[]>(
      `${this.apiUrl}/api/find`,
      { id }
    ).pipe(
      map(parkings => {
        if (parkings?.length) {
          return parkings[0];
        }
        throw new Error('Parking not found');
      })
    );
  }
}