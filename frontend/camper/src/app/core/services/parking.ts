import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Parking, SearchFilters } from '../models/parking';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class ParkingService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:5000';

  /**
   * Buscar parkings con filtro específico
   * POST /find
   */
  searchParkings(filters: SearchFilters): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/api/parking/search`);
  }

  /**
   * Ver detalles de un parking
   * Usa POST /find pasando el ID
   */
  getParkingById(id: string | number): Observable<Parking> {
    const filter = { id: id };

    return this.http.post<Parking[]>(`${this.apiUrl}/api/find`, filter).pipe(
      map(parkings => {
        if (parkings && parkings.length > 0) {
          return parkings[0];
        }
        throw new Error('Parking not found');
      })
    );
  }
}