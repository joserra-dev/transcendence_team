import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { BookingService } from '../../../core/services/booking';
import { BookingHistoryResponse } from '../../../core/models/booking';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-history',
  standalone: true,
  imports: [CommonModule, RouterLink, ReactiveFormsModule, TranslateModule],
  templateUrl: './history.html',
  styleUrls: ['./history.scss']
})
export class History implements OnInit {
  private bookingService = inject(BookingService);
  private fb = inject(FormBuilder);

  allBookings: BookingHistoryResponse[] = [];
  filteredBookings: BookingHistoryResponse[] = [];

  isLoading = true;
  errorMessage = '';

  showQrModal = false;
  currentQrCode: string | null = null;

  filterForm: FormGroup = this.fb.group({
    startDate: [''],
    endDate: [''],
    nombreParking: [''],
    estado: ['']
  });

  ngOnInit() {
    this.loadHistory();
  }

  loadHistory() {
    this.isLoading = true;
    this.bookingService.getHistory().subscribe({
      next: (data) => {
        this.allBookings = data.sort((a, b) => {
          return new Date(b.createDate).getTime() - new Date(a.createDate).getTime();
        });

        this.filteredBookings = [...this.allBookings];
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = 'HISTORY.ERROR_LOADING';
        this.isLoading = false;
      }
    });
  }

  applyFilters() {
    const filters = this.filterForm.value;

    this.filteredBookings = this.allBookings.filter(booking => {
      let matches = true;

      if (filters.startDate && booking.startDate) {
        matches = matches && this.extractDate(booking.startDate) >= this.extractDate(filters.startDate);
      }

      if (filters.endDate && booking.endDate) {
        matches = matches && this.extractDate(booking.endDate) <= this.extractDate(filters.endDate);
      }

      if (filters.nombreParking) {
        const searchStr = filters.nombreParking.toLowerCase();
        const pName = booking.parkingName ? booking.parkingName.toLowerCase() : '';
        matches = matches && pName.includes(searchStr);
      }

      if (filters.estado && filters.estado !== '') {
        matches = matches && booking.status === filters.estado;
      }

      return matches;
    });
  }

  clearFilters() {
    this.filterForm.reset({
        startDate: '',
        endDate: '',
        nombreParking: '',
        estado: ''
    });
    this.filteredBookings = [...this.allBookings];
  }

  getStatusLabel(estado: string): string {
    if (estado === '1') return 'HISTORY.CONFIRMED';
    if (estado === '2') return 'HISTORY.PROCESSING';
    if (estado === '3') return 'HISTORY.EXPIRED';
    return 'HISTORY.CANCELLED';
  }

  // Para las fechas del buscador
  openDatePicker(event: Event) {
    const input = event.target as HTMLInputElement;
    input.showPicker?.();
  }

  private extractDate(value: string): string {
    return value.split('T')[0].split(' ')[0];
  }

  onEntryDateChange() {
    const startDate = this.filterForm.get('startDate')?.value;
    if (startDate) {
      const nextDay = new Date(startDate);
      nextDay.setDate(nextDay.getDate() + 1);
      const nextDayStr = `${nextDay.getFullYear()}-${String(nextDay.getMonth() + 1).padStart(2, '0')}-${String(nextDay.getDate()).padStart(2, '0')}`;
      this.filterForm.patchValue({
        endDate: nextDayStr
      });
    }
  }
}
