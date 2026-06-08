export interface Plaza {
  id: number;
  nombre: string;
  esVip: boolean;
  tieneElectricidad: boolean;
  estado: string; // "0" = Libre, "1" = Ocupada
  precio: number;
  parkingNombre: string;
}

export interface Parking {
  id: number;
  nombre: string;

  web?: string;           
  telefono?: string;      
  email?: string;         
  personaContacto?: string;
  descripcion?: string;    

  municipio?: string;
  localidad?: string; 
  provincia?: string;
  
  tieneElectricidad?: boolean;
  tomaElectricidad?: boolean;
  
  tieneResiduales?: boolean;
  limpiezaAguasResiduales?: boolean;
  
  tieneVips?: boolean;
  plazasVip?: boolean;

  media?: number; 
  numeroPlazas?: number;
  
  plazas?: Plaza[];        
  plazasResponse?: Plaza[]; 
  
  activo?: boolean;
  imagen?: string; 
}

export interface SearchFilters {
  id?: number;

  fechaDesde?: string; 
  fechaHasta?: string; 
  localidad?: string;
  provincia?: string;
  tomaElectricidad?: boolean;
  limpiezaAguasResiduales?: boolean;
  plazasVip?: boolean;
}