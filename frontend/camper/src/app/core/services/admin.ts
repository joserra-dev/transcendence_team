import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { Parking, Space } from '../models/parking';
import { AdminUser, Company } from '../models/user';
import { AdminBooking, AdminBookingFilters } from '../models/booking';

@Injectable({
  providedIn: 'root',
})
export class Admin {

  private http = inject(HttpClient);

  private apiUrl = `${window.env.URL_BACK}/api/admin`;

  getParkings(companyId?: number): Observable<Parking[]> {
    const params = companyId != null ? { companyId: String(companyId) } : undefined;
    return this.http.get<Parking[]>(`${this.apiUrl}/parking`, { params });
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

  deleteParking(id: number): Observable<{ mensaje: string }> {
    return this.http.delete<{ mensaje: string }>(`${this.apiUrl}/parking/${id}`);
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

  getBookings(filters?: AdminBookingFilters): Observable<AdminBooking[]> {
    const params: Record<string, string> = {};
    if (filters?.parkingId != null) {
      params['parkingId'] = String(filters.parkingId);
    }
    if (filters?.status) {
      params['status'] = filters.status;
    }
    if (filters?.companyId != null) {
      params['companyId'] = String(filters.companyId);
    }
    return this.http.get<AdminBooking[]>(`${this.apiUrl}/bookings`, { params });
  }

  getBookingById(id: number): Observable<AdminBooking> {
    return this.http.get<AdminBooking>(`${this.apiUrl}/bookings/${id}`);
  }

  cancelBooking(id: number): Observable<{ mensaje: string }> {
    return this.http.put<{ mensaje: string }>(`${this.apiUrl}/bookings/${id}/cancel`, {});
  }

  getUsers(): Observable<AdminUser[]> {
    return this.http.get<AdminUser[]>(`${this.apiUrl}/users`);
  }

  getCompanies(): Observable<Company[]> {
    return this.http.get<Company[]>(`${this.apiUrl}/companies`);
  }

  createCompany(data: {
    name: string;
    cif?: string;
    adminEmail: string;
    adminPassword: string;
    adminNombre: string;
    adminApellidos?: string;
    adminDni?: string;
  }): Observable<Company> {
    return this.http.post<Company>(`${this.apiUrl}/companies`, data);
  }

  getCompany(id: number): Observable<Company> {
    return this.http.get<Company>(`${this.apiUrl}/companies/${id}`);
  }

  updateCompany(id: number, data: { name: string; cif?: string }): Observable<Company> {
    return this.http.put<Company>(`${this.apiUrl}/companies/${id}`, data);
  }

  deleteCompany(id: number): Observable<{ mensaje: string }> {
    return this.http.delete<{ mensaje: string }>(`${this.apiUrl}/companies/${id}`);
  }

  getCompanyUsers(companyId: number): Observable<AdminUser[]> {
    return this.http.get<AdminUser[]>(`${this.apiUrl}/companies/${companyId}/users`);
  }

  updateUser(userId: number, data: {
    email?: string;
    password?: string;
    nombre?: string;
    apellidos?: string;
    dni?: string;
    role?: string;
    companyId?: number | null;
  }): Observable<AdminUser> {
    return this.http.put<AdminUser>(`${this.apiUrl}/users/${userId}`, data);
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