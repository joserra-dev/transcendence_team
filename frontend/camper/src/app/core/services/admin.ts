import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { Parking, Plaza } from '../models/parking';

@Injectable({
  providedIn: 'root',
})
export class Admin {

  private http = inject(HttpClient);

  private apiUrl = `${window.env.URL_BACK}/api/admin`;

  getParkings(): Observable<Parking[]> {
    return this.http.get<Parking[]>(
      `${this.apiUrl}/parking`
    );
  }

  getParkingById(id: number): Observable<Parking> {
    return this.http.get<Parking>(
      `${this.apiUrl}/parking/${id}`
    );
  }

  createParking(parking: Partial<Parking>): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/parking`,
      parking
    );
  }

  updateParking(parking: Partial<Parking>): Observable<any> {
    return this.http.put(
      `${this.apiUrl}/parking`,
      parking
    );
  }

  createSpot(parkingId: number, spot: Partial<Plaza>): Observable<Plaza> {
    return this.http.post<Plaza>(
      `${this.apiUrl}/parking/${parkingId}/plazas`,
      spot
    );
  }

  updateSpot(
    parkingId: number,
    spotId: number,
    spot: Partial<Plaza>
  ): Observable<Plaza> {
    return this.http.put<Plaza>(
      `${this.apiUrl}/parking/${parkingId}/plazas/${spotId}`,
      spot
    );
  }

  getSpotById(spotId: number): Observable<Plaza> {
    return this.http.get<Plaza>(
      `${this.apiUrl}/parking/plaza/${spotId}`
    );
  }
}