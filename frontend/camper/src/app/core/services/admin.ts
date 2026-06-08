import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Parking, Plaza } from '../models/parking';

@Injectable({
  providedIn: 'root',
})
export class Admin {

  private http = inject(HttpClient);
  private apiUrl = 'https://camperapi.onrender.com/api/admin';

  /**
   * Obtener la lista de parkings de la empresa
   * GET /api/admin/parking
   */
  getParkings(): Observable<Parking[]> {
    return this.http.get<Parking[]>(`${this.apiUrl}/parking`);
  }

  /**
   * Obtener datos detallados de un parking específico
   * GET /api/admin/parking/{id}
   */
  getParkingById(id: number): Observable<Parking> {
    return this.http.get<Parking>(`${this.apiUrl}/parking/${id}`);
  }

  /**
   * Crear un nuevo parking en la empresa
   * POST /api/admin/parking
   */
  createParking(parking: Partial<Parking>): Observable<any> {
    return this.http.post(`${this.apiUrl}/parking`, parking);
  }

  /**
   * Actualizar los datos de un parking existente
   * PUT /api/admin/parking
   */
  updateParking(parking: Partial<Parking>): Observable<any> {
    return this.http.put(`${this.apiUrl}/parking`, parking);
  }


  /**
   * Dar de alta una nueva plaza en un parking
   * POST /api/admin/parking/{parkingId}/plazas
   */
  createSpot(parkingId: number, spot: Partial<Plaza>): Observable<Plaza> {
    return this.http.post<Plaza>(`${this.apiUrl}/parking/${parkingId}/plazas`, spot);
  }

  /**
   * Actualizar los datos de una plaza existente
   * PUT /api/admin/parking/{parkingId}/plazas/{plazaId}
   */
  updateSpot(parkingId: number, spotId: number, spot: Partial<Plaza>): Observable<Plaza> {
    return this.http.put<Plaza>(`${this.apiUrl}/parking/${parkingId}/plazas/${spotId}`, spot);
  }

  /**
   * Obtener los datos de una plaza específica
   * GET /api/admin/parking/plaza/{id}
   */
  getSpotById(spotId: number): Observable<Plaza> {
    return this.http.get<Plaza>(`${this.apiUrl}/parking/plaza/${spotId}`);
  }
}
