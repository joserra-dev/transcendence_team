export interface MetricsChartItem {
  label: string;
  value: number;
}

export interface CompanyMetrics {
  companyId: number;
  companyName: string;
  year: number;
  totals: {
    sales: number;
    bookings: number;
  };
  bookingsByParking: MetricsChartItem[];
  salesByMonth: MetricsChartItem[];
}

export interface MetricsFilters {
  year: number;
}
