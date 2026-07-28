export interface User {
  id: number;
  nombrePersona: string;
  apellidosPersona: string;
  fecNacimientoPersona: string;
  dniPersona: string;
  //ibanPersona: string;
  metodoPago?: string;
  tarjeta?: string;
  emailPersona: string | null;
  empresaNombre: string | null;
  admin: boolean;
  role?: 'user' | 'admin' | 'super_admin';
  companyId?: number | null;
}

export interface AdminUser {
  id: number;
  email: string;
  isVerified: boolean;
  nombre: string;
  apellidos: string;
  dni: string;
  role: string;
  companyId: number | null;
  companyName: string | null;
}

export interface Company {
  id: number;
  name: string;
  cif?: string;
  parkingCount?: number;
  adminUserId?: number | null;
  adminEmail?: string | null;
  adminName?: string | null;
  adminApellidos?: string | null;
  adminDni?: string | null;
}