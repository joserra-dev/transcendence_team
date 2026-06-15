export interface Space {
  id: number;
  name: string;
  isVip: boolean;
  hasElectr: boolean;
  status: string;
  price: number;
  parkingName: string;
  id_parking: number;
}

export interface Parking {
  id: number;
  name: string;

  web?: string;           
  telephone?: string;      
  email?: string;         
  contact_person?: string;
  descripcion?: string;    

  municipality?: string;
  localidad?: string; 
  province?: string;
  
  has_electricity?: boolean;
  tomaElectricidad?: boolean;
  
  has_waste_disposal?: boolean;
  limpiezaAguasResiduales?: boolean;
  
  has_vip_spots?: boolean;
  plazasVip?: boolean;

  media?: number; 
  numeroPlazas?: number;
  
  spaces?: Space[];        
  plazasResponse?: Space[]; 
  
  isActive?: boolean;
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