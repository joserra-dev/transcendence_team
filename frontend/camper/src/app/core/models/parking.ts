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
  id_company?: number;
  name: string;

  web?: string;           
  telephone?: string;      
  email?: string;         
  contact_person?: string;
  
  description?: string;
  
  longitude?: number;
  latitude?: number;
  
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

  startDate?: string;
  endDate?: string;
  localidad?: string;
  provincia?: string;
  tomaElectricidad?: boolean;
  limpiezaAguasResiduales?: boolean;
  plazasVip?: boolean;

  page?: number;
  limit?: number;
  sort?: string;
  order?: 'asc' | 'desc';
}

export interface ParkingPage {
  items: Parking[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}