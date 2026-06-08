export interface Booking {
  id: number;
  fecAlta: string; 
  fecInicio: string;
  fecFin: string;
  parkingNombre: string;
  estado: string;
  plazaNombre?: string; 
  precioTotal?: number;
  qrData?: string; 
}

export interface BookingFilters {
  fechaDesde?: string;
  fechaHasta?: string;
  nombreParking?: string;
  estado?: string;
}

export interface BookingRequest {
  idPlaza: number;
  idParking: number;
  fecInicio: string; 
  fecFin: string;    
}

export interface BookingHistoryResponse {
  id: number;
  usuarioId: number;
  usuarioEmail: string;
  plazaId: number;
  parkingId: number;
  parkingNombre: string;
  precio: number;
  precioTotal: number;
  fecInicio: string | null;
  fecFin: string | null;
  fecAlta: string;
  estado: string;
  puntuacion: number | null;
}