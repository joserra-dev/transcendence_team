import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ParkingService } from '../../../core/services/parking';
import { Parking, SearchFilters } from '../../../core/models/parking';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { finalize } from 'rxjs/operators';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-search-parking',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink, TranslateModule],
  templateUrl: './search-parking.html',
  styleUrls: ['./search-parking.scss']
})
export class SearchParking implements OnInit, OnDestroy {
  private parkingService = inject(ParkingService);
  private fb = inject(FormBuilder);
  private translate = inject(TranslateService); // Inyectamos el servicio de traducción

  parkings: Parking[] = [];
  isLoading = false;
  errorMessage = '';
  
  // Variables para controlar el formato regional
  dateFormat: string = 'dd/MM/yyyy';
  private langFormatSub!: Subscription;

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
    // 1. Suscripción al cambio de idioma
    this.langFormatSub = this.translate.onLangChange.subscribe((event) => {
      this.dateformatdefine(event.lang);
    });

    // 2. Establecer formato inicial
    this.dateformatdefine(this.translate.currentLang || this.translate.defaultLang || 'es');

    const today = new Date().toISOString().split('T')[0];
    const tomorrow = new Date(new Date().setDate(new Date().getDate() + 1)).toISOString().split('T')[0];

    this.searchForm.patchValue({
      fechaDesde: today,
      fechaHasta: tomorrow
    });

    this.onSearch();
  }

  private dateformatdefine(lang: string) {
    const idioma = lang.toLowerCase();
    if (idioma === 'eu' || idioma === 'en') {
      this.dateFormat = 'yyyy/MM/dd';
    } else {
      this.dateFormat = 'dd/MM/yyyy';
    }
  }

  // Getters auxiliares para leer cómodamente el valor ISO crudo desde el HTML
  get rawEntryDate(): string {
    return this.searchForm.get('fechaDesde')?.value || '';
  }

  get rawExitDate(): string {
    return this.searchForm.get('fechaHasta')?.value || '';
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
    if (!parking.spaces || parking.spaces.length === 0) return 0;
    return Math.min(...parking.spaces.map(p => p.price));
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

  // Abre el selector nativo del input oculto subyacente o un datepicker personalizado
  openDatePicker(hiddenInput: HTMLInputElement) {
    hiddenInput.showPicker?.();
  }

  onEntryDateChange() {
    const fechaDesde = this.searchForm.get('fechaDesde')?.value;
    if (fechaDesde) {
      const nextDay = new Date(fechaDesde);
      nextDay.setDate(nextDay.getDate() + 1);
      this.searchForm.patchValue({
        fechaHasta: nextDay.toISOString().split('T')[0]
      });
    }
  }

  getServices(parking: Parking): string[] {
    const services: string[] = [];

    if (parking.has_electricity) {
      services.push('SEARCH.ELECTRICITY');
    }

    if (parking.has_waste_disposal) {
      services.push('SEARCH.RESIDUALS');
    }

    if (parking.has_vip_spots) {
      services.push('SEARCH.VIP');
    }

    return services;
  }

  ngOnDestroy() {
    if (this.langFormatSub) {
      this.langFormatSub.unsubscribe();
    }
  }
}