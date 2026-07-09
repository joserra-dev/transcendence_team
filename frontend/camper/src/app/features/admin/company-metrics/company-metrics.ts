import { ChangeDetectorRef, Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { Admin } from '../../../core/services/admin';
import { CompanyMetrics, MetricsChartItem } from '../../../core/models/metrics';

interface DonutSlice extends MetricsChartItem {
  color: string;
  start: number;
  end: number;
  percent: number;
}

@Component({
  selector: 'app-company-metrics',
  imports: [CommonModule, FormsModule, RouterLink, TranslateModule],
  templateUrl: './company-metrics.html',
  styleUrl: './company-metrics.scss',
})
export class CompanyMetricsPage implements OnInit {
  private adminService = inject(Admin);
  private route = inject(ActivatedRoute);
  private cdr = inject(ChangeDetectorRef);

  companyId: number | null = null;
  isSuperAdminView = false;
  metrics: CompanyMetrics | null = null;
  isLoading = true;
  errorMessage = '';
  year = new Date().getFullYear();
  availableYears: number[] = [new Date().getFullYear()];

  readonly chartColors = ['#4F46E5', '#059669', '#F59E0B', '#EC4899', '#8B5CF6', '#006299', '#8A9C3B', '#6B7280'];

  ngOnInit() {
    const idParam = this.route.snapshot.paramMap.get('id');
    this.isSuperAdminView = !!idParam;
    this.companyId = idParam ? Number(idParam) : null;
    this.loadMetrics();
  }

  get backLink(): string[] {
    if (this.isSuperAdminView && this.companyId) {
      return ['/admin/companies', String(this.companyId), 'edit'];
    }
    return ['/admin/dashboard'];
  }

  get pageTitle(): string {
    return this.metrics?.companyName || '';
  }

  get totalSales(): number {
    return this.metrics?.totals?.sales ?? 0;
  }

  get totalBookings(): number {
    return this.metrics?.totals?.bookings ?? 0;
  }

  get formattedSales(): string {
    return `${this.totalSales.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} €`;
  }

  get bookingsSlices(): DonutSlice[] {
    return this.buildSlices(this.metrics?.bookingsByParking ?? []);
  }

  get salesSlices(): DonutSlice[] {
    return this.buildSlices(this.metrics?.salesByMonth ?? []);
  }

  get bookingsGradient(): string {
    return this.buildGradient(this.bookingsSlices);
  }

  get salesGradient(): string {
    return this.buildGradient(this.salesSlices);
  }

  applyFilters() {
    this.loadMetrics();
  }

  loadMetrics() {
    this.isLoading = true;
    this.errorMessage = '';

    const request = this.isSuperAdminView && this.companyId
      ? this.adminService.getCompanyMetrics(this.companyId, { year: this.year })
      : this.adminService.getOwnCompanyMetrics({ year: this.year });

    request.subscribe({
      next: (metrics) => {
        this.metrics = metrics;
        this.availableYears = metrics.availableYears ?? [metrics.year];
        this.year = metrics.year;
        this.isLoading = false;
        this.refreshView();
      },
      error: () => {
        this.errorMessage = 'ADMIN_METRICS.ERRORS.LOAD';
        this.isLoading = false;
        this.refreshView();
      },
    });
  }

  formatValue(value: number, isCurrency = false): string {
    if (isCurrency) {
      return `${value.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} €`;
    }
    return String(value);
  }

  private refreshView() {
    this.cdr.detectChanges();
    queueMicrotask(() => this.cdr.detectChanges());
  }

  private buildSlices(items: MetricsChartItem[]): DonutSlice[] {
    const total = items.reduce((sum, item) => sum + item.value, 0);
    if (total <= 0) {
      return [];
    }

    let angle = 0;
    return items.map((item, index) => {
      const sweep = (item.value / total) * 360;
      const start = angle;
      angle += sweep;
      return {
        ...item,
        color: this.chartColors[index % this.chartColors.length],
        start,
        end: angle,
        percent: Math.round((item.value / total) * 100),
      };
    });
  }

  private buildGradient(slices: DonutSlice[]): string {
    if (!slices.length) {
      return 'conic-gradient(#D1D5DB 0deg 360deg)';
    }
    return `conic-gradient(${slices
      .map((slice) => `${slice.color} ${slice.start}deg ${slice.end}deg`)
      .join(', ')})`;
  }
}
