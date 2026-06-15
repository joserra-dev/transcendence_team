import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { Booking, BookingHistoryResponse, BookingRequest } from '../models/booking';

@Injectable({
  providedIn: 'root'
})
export class BookingService {
  private http = inject(HttpClient);

  private apiUrl = `${window.env.URL_BACK}/api`;

  /**
   * Ver historial de reservas completo
   */
  getHistory(): Observable<BookingHistoryResponse[]> {
    return this.http.get<BookingHistoryResponse[]>(
      `${this.apiUrl}/historic/list`
    );
  }

  /**
   * Ver detalles de reserva específica
   */
  getBookingById(id: string | number): Observable<Booking> {
    return this.http.get<Booking>(
      `${this.apiUrl}/booking/${id}`
    );
  }

  /**
   * Cancelar reserva
   */
  cancelBooking(id: number): Observable<any> {
    return this.http.put(
      `${this.apiUrl}/booking/cancel`,
      { idReserva: id }
    );
  }

  /**
   * Realizar reserva
   */
  createBooking(bookingData: BookingRequest): Observable<any> {
    return this.http.post(
      `${this.apiUrl}/booking`,
      bookingData,
      { responseType: 'text' }
    );
  }

  /**
   * Obtener QR de la reserva
   */
  getQrCode(id: number): Observable<string> {
    return this.http.post<{ qrBase64: string }>(
      `${this.apiUrl}/booking/qr`,
      { idReserva: id }
    ).pipe(
      map(response => response.qrBase64)
    );
  }

  /**
   * Puntuar una reserva
   */
  rateBooking(id: number, score: number): Observable<any> {
    return this.http.put(
      `${this.apiUrl}/booking/rate`,
      { idReserva: id, puntuacion: score }
    );
  }
}