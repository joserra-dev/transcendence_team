import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { Parking, Space } from '../models/parking';

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

  createSpot(parkingId: number, spot: Partial<Space>): Observable<Space> {
    return this.http.post<Space>(
      `${this.apiUrl}/parking/${parkingId}/space`,
      spot
    );
  }

  updateSpot(
    parkingId: number,
    spotId: number,
    spot: Partial<Space>
  ): Observable<Space> {
    return this.http.put<Space>(
      `${this.apiUrl}/parking/${parkingId}/space/${spotId}`,
      spot
    );
  }

  getSpotById(spotId: number): Observable<Space> {
    return this.http.get<Space>(
      `${this.apiUrl}/parking/space/${spotId}`
    );
  }
}