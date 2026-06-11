import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { Parking, SearchFilters } from '../models/parking';

@Injectable({
  providedIn: 'root'
})
export class ParkingService {
  private http = inject(HttpClient);

  private apiUrl = `${window.env.URL_BACK}`;

  searchParkings(filters: SearchFilters): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/api/parking/search`);
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