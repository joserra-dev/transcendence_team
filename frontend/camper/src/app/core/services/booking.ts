import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Booking, BookingHistoryResponse, BookingRequest } from '../models/booking';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class BookingService {
  private http = inject(HttpClient);
  private apiUrl = 'https://camperapi.onrender.com/api';

  /**
   * Ver historial de reservas completo
   * GET /historico/listado
   */
  getHistory(): Observable<BookingHistoryResponse[]> {
    return this.http.get<BookingHistoryResponse[]>(`${this.apiUrl}/historico/listado`);
  }

  /**
   * Ver detalles de reserva específica
   * GET /reserva/:id
   */
  getBookingById(id: string | number): Observable<Booking> {
    return this.http.get<Booking>(`${this.apiUrl}/reserva/${id}`);
  }

  /**
   * Cancelar reserva
   */
  cancelBooking(id: number): Observable<any> {
    const body = { idReserva: id };
    return this.http.put(`${this.apiUrl}/reserva/cancelar`, body);
  }

  /**
   * Realizar reserva
   * POST /public/reserva
   */
  createBooking(bookingData: BookingRequest): Observable<any> {
    return this.http.post(`${this.apiUrl}/reserva`, bookingData, { responseType: 'text' });
  }

  /**
   * Obtener QR de la reserva
   * POST /reserva/qr
   */
  getQrCode(id: number): Observable<string> {
    const body = { idReserva: id };
    return this.http.post<{ qrBase64: string }>(`${this.apiUrl}/reserva/qr`, body).pipe(
      map(response => response.qrBase64) 
    );
  }

  /**
   * Puntuar una reserva
   * PUT /reserva/puntuar
   */
  rateBooking(id: number, score: number): Observable<any> {
    const body = { idReserva: id, puntuacion: score };
    return this.http.put(`${this.apiUrl}/reserva/puntuar`, body);
  }
}