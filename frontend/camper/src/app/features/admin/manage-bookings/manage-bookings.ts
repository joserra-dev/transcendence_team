import { Component, ElementRef, OnInit, ViewChild, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { Admin } from '../../../core/services/admin';
import { Auth } from '../../../core/services/auth';
import { AdminBooking } from '../../../core/models/booking';
import { Parking } from '../../../core/models/parking';
import { ConfirmDialog } from '../../../shared/components/confirm-dialog/confirm-dialog';

@Component({
  selector: 'app-manage-bookings',
  imports: [CommonModule, ReactiveFormsModule, RouterLink, TranslateModule, ConfirmDialog],
  templateUrl: './manage-bookings.html',
  styleUrl: './manage-bookings.scss',
})
export class ManageBookings implements OnInit {
  @ViewChild('bookingsListScroll') bookingsListScroll?: ElementRef<HTMLElement>;

  private adminService = inject(Admin);
  private authService = inject(Auth);
  private fb = inject(FormBuilder);

  readonly pageSize = 8;

  allBookings: AdminBooking[] = [];
  filteredBookings: AdminBooking[] = [];
  parkings: Parking[] = [];
  currentPage = 1;
  isLoading = true;
  errorMessage = '';
  successMessage = '';
  cancellingId: number | null = null;
  showCancelConfirm = false;
  cancelConfirmParams: Record<string, string | number> = {};
  private bookingPendingCancel: AdminBooking | null = null;

  filterForm: FormGroup = this.fb.group({
    startDate: [''],
    endDate: [''],
    parkingId: [''],
    status: [''],
    licensePlate: [''],
  });

  ngOnInit() {
    this.loadParkings();
    this.loadBookings();
  }

  get totalPages(): number {
    return Math.max(1, Math.ceil(this.filteredBookings.length / this.pageSize));
  }

  get paginatedBookings(): AdminBooking[] {
    const start = (this.currentPage - 1) * this.pageSize;
    return this.filteredBookings.slice(start, start + this.pageSize);
  }

  get pageRangeStart(): number {
    if (this.filteredBookings.length === 0) {
      return 0;
    }
    return (this.currentPage - 1) * this.pageSize + 1;
  }

  get pageRangeEnd(): number {
    return Math.min(this.currentPage * this.pageSize, this.filteredBookings.length);
  }

  loadParkings() {
    this.adminService.getParkings().subscribe({
      next: (data) => {
        this.parkings = data;
      },
      error: () => {},
    });
  }

  loadBookings() {
    this.isLoading = true;
    this.errorMessage = '';

    const filters = this.filterForm.value;
    this.adminService.getBookings({
      parkingId: filters.parkingId ? Number(filters.parkingId) : undefined,
      status: filters.status || undefined,
    }).subscribe({
      next: (data) => {
        this.allBookings = data;
        this.applyLocalFilters();
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'ADMIN_BOOKINGS.ERRORS.LOAD';
        this.isLoading = false;
      },
    });
  }

  applyFilters() {
    this.currentPage = 1;
    this.loadBookings();
  }

  applyLocalFilters() {
    const filters = this.filterForm.value;

    this.filteredBookings = this.allBookings.filter((booking) => {
      let matches = true;

      if (filters.fechaDesde && booking.startDate) {
        matches = matches && this.extractDate(booking.startDate) >= this.extractDate(filters.fechaDesde);
      }

      if (filters.fechaHasta && booking.endDate) {
        matches = matches && this.extractDate(booking.endDate) <= this.extractDate(filters.fechaHasta);
      }

      if (filters.licensePlate) {
        const search = filters.licensePlate.toLowerCase();
        matches = matches && (booking.licensePlate || '').toLowerCase().includes(search);
      }

      return matches;
    });

    this.clampCurrentPage();
  }

  clearFilters() {
    this.filterForm.reset({
      startDate: '',
      endDate: '',
      parkingId: '',
      status: '',
      licensePlate: '',
    });
    this.currentPage = 1;
    this.loadBookings();
  }

  cancelBooking(event: Event, booking: AdminBooking) {
    event.stopPropagation();
    if (booking.status === '0' || this.cancellingId != null) {
      return;
    }

    this.bookingPendingCancel = booking;
    this.cancelConfirmParams = {
      ref: booking.id,
      parking: booking.parkingName || '',
    };
    this.showCancelConfirm = true;
  }

  dismissCancelBooking() {
    this.showCancelConfirm = false;
    this.bookingPendingCancel = null;
  }

  confirmCancelBooking() {
    const booking = this.bookingPendingCancel;
    if (!booking || booking.status === '0' || this.cancellingId != null) {
      return;
    }

    this.showCancelConfirm = false;
    this.bookingPendingCancel = null;
    this.cancellingId = booking.id;
    this.errorMessage = '';
    this.successMessage = '';

    this.adminService.cancelBooking(booking.id).subscribe({
      next: () => {
        booking.status = '0';
        this.successMessage = 'ADMIN_BOOKINGS.SUCCESS_CANCEL';
        this.cancellingId = null;
      },
      error: (err) => {
        this.errorMessage = err.error?.error || 'ADMIN_BOOKINGS.ERRORS.CANCEL';
        this.cancellingId = null;
      },
    });
  }

  getStatusLabel(status: string): string {
    return status === '1' ? 'HISTORY.CONFIRMED' : 'HISTORY.CANCELLED';
  }

  exportCsv() {
    if (this.filteredBookings.length === 0) {
      return;
    }

    const headers = [
      'ID',
      'Parking',
      'Cliente',
      'Email',
      'Matrícula',
      'Plaza',
      'Inicio',
      'Fin',
      'Total',
      'Estado',
    ];

    const rows = this.filteredBookings.map((b) => [
      b.id,
      b.parkingName ?? '',
      b.userName ?? '',
      b.userEmail ?? '',
      b.licensePlate ?? '',
      b.spaceName ?? '',
      b.startDate ?? '',
      b.endDate ?? '',
      b.totalPrice ?? '',
      b.status === '1' ? 'Confirmada' : 'Cancelada',
    ]);

    const csv = [headers, ...rows]
      .map((row) => row.map((cell) => this.escapeCsvCell(cell)).join(';'))
      .join('\r\n');

    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `reservas_${new Date().toISOString().slice(0, 10)}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }

  private escapeCsvCell(value: string | number): string {
    const text = String(value);
    if (/[";\r\n]/.test(text)) {
      return `"${text.replace(/"/g, '""')}"`;
    }
    return text;
  }

  goToPage(page: number) {
    if (page < 1 || page > this.totalPages || page === this.currentPage) {
      return;
    }
    this.currentPage = page;
    this.bookingsListScroll?.nativeElement.scrollTo({ top: 0, behavior: 'smooth' });
  }

  prevPage() {
    this.goToPage(this.currentPage - 1);
  }

  nextPage() {
    this.goToPage(this.currentPage + 1);
  }

  openDatePicker(event: Event) {
    const input = event.target as HTMLInputElement;
    input.showPicker?.();
  }

  private extractDate(value: string): string {
    return value.split('T')[0].split(' ')[0];
  }

  private clampCurrentPage() {
    if (this.currentPage > this.totalPages) {
      this.currentPage = this.totalPages;
    }
  }
}
