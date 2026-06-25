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
  idSpace: number;
  idParking: number;
  startDate: string; 
  endDate: string;
  licensePlate: string;    
}

export interface BookingHistoryResponse {
  id: number;
  userId: number;
  userEmail: string;
  spaceId: number;
  parkingId: number;
  parkingName: string;
  price: number;
  totalPrice: number;
  startDate: string | null;
  endDate: string | null;
  createDate: string;
  status: string;
  range: number | null;
  licensePlate?: string;
}

export interface AdminBooking {
  id: number;
  userId: number;
  userEmail: string;
  userName: string;
  spaceId: number;
  spaceName: string;
  parkingId: number;
  parkingName: string;
  price: number;
  totalPrice: number;
  startDate: string | null;
  endDate: string | null;
  createDate: string;
  status: string;
  rating: number | null;
  licensePlate: string;
}

export interface AdminBookingFilters {
  parkingId?: number;
  status?: string;
  companyId?: number;
}