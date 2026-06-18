import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { Parking, Space } from '../models/parking';
import { AdminUser, Company } from '../models/user';

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

  getUsers(): Observable<AdminUser[]> {
    return this.http.get<AdminUser[]>(`${this.apiUrl}/users`);
  }

  getCompanies(): Observable<Company[]> {
    return this.http.get<Company[]>(`${this.apiUrl}/companies`);
  }

  createUser(data: {
    email: string;
    password: string;
    nombre: string;
    apellidos: string;
    dni: string;
    role: string;
    companyId?: number | null;
  }): Observable<{ mensaje: string; id: number }> {
    return this.http.post<{ mensaje: string; id: number }>(`${this.apiUrl}/users`, data);
  }

  updateUserRole(userId: number, data: { role: string; companyId?: number | null }): Observable<{ mensaje: string }> {
    return this.http.put<{ mensaje: string }>(`${this.apiUrl}/users/${userId}/role`, data);
  }
}