import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MetricsChartItem } from '../../../core/models/metrics';

@Component({
  selector: 'app-donut-chart',
  imports: [CommonModule],
  templateUrl: './donut-chart.html',
  styleUrl: './donut-chart.scss',
})
export class DonutChart {
  @Input() items: MetricsChartItem[] = [];
  @Input() emptyLabel = 'Sin datos';
  @Input() isCurrency = false;

  readonly colors = ['#4F46E5', '#059669', '#F59E0B', '#EC4899', '#8B5CF6', '#006299', '#8A9C3B', '#6B7280'];

  get hasData(): boolean {
    return this.items.length > 0 && this.items.some((item) => item.value > 0);
  }

  get slices() {
    const total = this.items.reduce((sum, item) => sum + item.value, 0);
    if (total <= 0) {
      return [];
    }

    let angle = 0;
    return this.items.map((item, index) => {
      const sweep = (item.value / total) * 360;
      const start = angle;
      angle += sweep;
      return {
        ...item,
        color: this.colors[index % this.colors.length],
        start,
        end: angle,
        percent: Math.round((item.value / total) * 100),
      };
    });
  }

  get gradient(): string {
    if (!this.hasData) {
      return 'conic-gradient(#D1D5DB 0deg 360deg)';
    }
    return `conic-gradient(${this.slices
      .map((slice) => `${slice.color} ${slice.start}deg ${slice.end}deg`)
      .join(', ')})`;
  }

  formatValue(value: number): string {
    if (this.isCurrency) {
      return `${value.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} €`;
    }
    return String(value);
  }
}
