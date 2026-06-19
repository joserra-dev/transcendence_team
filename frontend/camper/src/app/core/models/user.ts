export interface User {
  id: number;
  nombrePersona: string;
  apellidosPersona: string;
  fecNacimientoPersona: string;
  dniPersona: string;
  ibanPersona: string;
  metodoPago?: string;
  tarjeta?: string;
  emailPersona: string | null;
  avatar?: string;
  empresaNombre: string | null;
  admin: boolean;
}