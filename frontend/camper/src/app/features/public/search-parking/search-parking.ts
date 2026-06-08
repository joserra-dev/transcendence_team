import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ParkingService } from '../../../core/services/parking';
import { Parking, SearchFilters } from '../../../core/models/parking';
import { TranslateModule } from '@ngx-translate/core';
import { finalize } from 'rxjs/operators';

@Component({
  selector: 'app-search-parking',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink, TranslateModule],
  templateUrl: './search-parking.html',
  styleUrls: ['./search-parking.scss']
})
export class SearchParking implements OnInit {
  private parkingService = inject(ParkingService);
  private fb = inject(FormBuilder);

  parkings: Parking[] = [];
  isLoading = false;
  errorMessage = '';

  searchForm: FormGroup = this.fb.group({
    fechaDesde: [''],
    fechaHasta: [''],
    localidad: [''],
    provincia: [''],
    tomaElectricidad: [false],
    limpiezaAguasResiduales: [false],
    plazasVip: [false]
  });

  ngOnInit() {
    const today = new Date().toISOString().split('T')[0];
    const tomorrow = new Date(new Date().setDate(new Date().getDate() + 1)).toISOString().split('T')[0];

    this.searchForm.patchValue({
      fechaDesde: today,
      fechaHasta: today
    });

    this.onSearch();
  }

  onSearch() {
    if (this.searchForm.invalid) {
      this.searchForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    const formVal = this.searchForm.value;

    const filters: any = {
      fechaDesde: formVal.fechaDesde,
      fechaHasta: formVal.fechaHasta,
    };

    if (formVal.localidad && formVal.localidad.trim() !== '') {
      filters.localidad = formVal.localidad.trim();
    }

    if (formVal.provincia && formVal.provincia.trim() !== '') {
      filters.provincia = formVal.provincia.trim();
    }

    if (formVal.tomaElectricidad) {
      filters.tomaElectricidad = true;
    }

    if (formVal.limpiezaAguasResiduales) {
      filters.limpiezaAguasResiduales = true;
    }

    if (formVal.plazasVip) {
      filters.plazasVip = true;
    }

    this.parkingService.searchParkings(filters)
      .pipe(finalize(() => this.isLoading = false))
      .subscribe({
        next: (data) => {
          this.parkings = data;
          if (this.parkings.length === 0) {
            this.errorMessage = 'SEARCH.ERRORS.NO_RESULTS';
          }
        },
        error: (err) => {
          console.error(err);
          this.errorMessage = 'SEARCH.ERRORS.CONNECTION';
        }
      });
  }

  getMinPrice(parking: Parking): number {
    if (!parking.plazas || parking.plazas.length === 0) return 0;
    return Math.min(...parking.plazas.map(p => p.precio));
  }

  clearFilters() {
    const currentDates = {
      fechaDesde: this.searchForm.get('fechaDesde')?.value,
      fechaHasta: this.searchForm.get('fechaHasta')?.value
    };

    this.searchForm.reset({
      ...currentDates,
      localidad: '',
      provincia: '',
      tomaElectricidad: false,
      limpiezaAguasResiduales: false,
      plazasVip: false
    });
    this.onSearch();
  }

  // Para las fechas del buscador
  openDatePicker(event: Event) {
    const input = event.target as HTMLInputElement;
    input.showPicker?.();
  }

  // Para los servicios en las tarjetas de los parking
  getServices(parking: Parking): string[] {
    const services: string[] = [];

    if (parking.tieneElectricidad) {
      services.push('SEARCH.ELECTRICITY');
    }

    if (parking.tieneResiduales) {
      services.push('SEARCH.RESIDUALS');
    }

    if (parking.tieneVips) {
      services.push('SEARCH.VIP');
    }

    return services;
  }
}
