import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { Admin } from '../../../core/services/admin';
import { Parking } from '../../../core/models/parking';
import { AdminBooking } from '../../../core/models/booking';

interface CalendarCell {
  date: string;
  dayNum: number;
  status: 'occupied' | 'blocked' | 'free';
  isPast: boolean;
}

@Component({
  selector: 'app-admin-calendar',
  imports: [CommonModule, FormsModule, RouterLink, TranslateModule],
  templateUrl: './calendar.html',
  styleUrl: './calendar.scss',
})
export class Calendar implements OnInit {
  private adminService = inject(Admin);

  readonly weekdays = [1, 2, 3, 4, 5, 6, 7];

  parkings: Parking[] = [];
  selectedParkingId: number | null = null;

  year!: number;
  month!: number;

  weeks: (CalendarCell | null)[][] = [];
  private blockedDays = new Set<string>();
  private occupiedMap = new Map<string, AdminBooking[]>();

  isLoading = false;
  errorMessage = '';

  selectedDay: string | null = null;
  selectedDayBookings: AdminBooking[] = [];

  ngOnInit() {
    const now = new Date();
    this.year = now.getFullYear();
    this.month = now.getMonth() + 1;
    this.loadParkings();
  }

  loadParkings() {
    this.adminService.getParkings().subscribe({
      next: (data) => {
        this.parkings = data;
      },
      error: () => {
        this.errorMessage = 'ADMIN_CALENDAR.ERRORS.LOAD_PARKINGS';
      },
    });
  }

  onParkingChange() {
    this.selectedDay = null;
    this.selectedDayBookings = [];
    this.loadCalendar();
  }

  get selectedParkingName(): string {
    return this.parkings.find((p) => p.id === this.selectedParkingId)?.name || '';
  }

  loadCalendar() {
    if (this.selectedParkingId == null) {
      this.weeks = [];
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    this.adminService.getParkingCalendar(this.selectedParkingId, this.year, this.month).subscribe({
      next: (data) => {
        this.blockedDays = new Set(data.blockedDays || []);
        this.occupiedMap = this.buildOccupancy(data.bookings || []);
        this.buildGrid();
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'ADMIN_CALENDAR.ERRORS.LOAD_CALENDAR';
        this.isLoading = false;
      },
    });
  }

  private buildOccupancy(bookings: AdminBooking[]): Map<string, AdminBooking[]> {
    const map = new Map<string, AdminBooking[]>();
    for (const booking of bookings) {
      if (!booking.startDate || !booking.endDate) {
        continue;
      }
      const start = this.parseDate(booking.startDate);
      const end = this.parseDate(booking.endDate);
      // Ocupa las noches [start, end)
      for (let d = new Date(start); d < end; d.setDate(d.getDate() + 1)) {
        const key = this.formatDate(d);
        const list = map.get(key) || [];
        list.push(booking);
        map.set(key, list);
      }
    }
    return map;
  }

  private buildGrid() {
    const firstOfMonth = new Date(this.year, this.month - 1, 1);
    const daysInMonth = new Date(this.year, this.month, 0).getDate();
    const leadingBlanks = (firstOfMonth.getDay() + 6) % 7; // Lunes primero

    const today = this.formatDate(new Date());
    const cells: (CalendarCell | null)[] = [];

    for (let i = 0; i < leadingBlanks; i++) {
      cells.push(null);
    }

    for (let day = 1; day <= daysInMonth; day++) {
      const date = this.formatDate(new Date(this.year, this.month - 1, day));
      let status: CalendarCell['status'] = 'free';
      if (this.occupiedMap.has(date)) {
        status = 'occupied';
      } else if (this.blockedDays.has(date)) {
        status = 'blocked';
      }
      cells.push({
        date,
        dayNum: day,
        status,
        isPast: date < today,
      });
    }

    while (cells.length % 7 !== 0) {
      cells.push(null);
    }

    const weeks: (CalendarCell | null)[][] = [];
    for (let i = 0; i < cells.length; i += 7) {
      weeks.push(cells.slice(i, i + 7));
    }
    this.weeks = weeks;
  }

  onDayClick(cell: CalendarCell | null) {
    if (!cell || this.selectedParkingId == null) {
      return;
    }

    if (cell.status === 'occupied') {
      this.selectedDay = cell.date;
      this.selectedDayBookings = this.occupiedMap.get(cell.date) || [];
      return;
    }

    if (cell.status === 'blocked') {
      this.unblockDay(cell.date);
      return;
    }

    this.blockDay(cell.date);
  }

  private blockDay(date: string) {
    if (this.selectedParkingId == null) {
      return;
    }
    this.errorMessage = '';
    // Actualización optimista: se pinta al instante y se revierte si falla.
    this.blockedDays.add(date);
    this.buildGrid();
    this.adminService.blockDay(this.selectedParkingId, date).subscribe({
      error: (err) => {
        this.blockedDays.delete(date);
        this.buildGrid();
        this.errorMessage = err.error?.error || 'ADMIN_CALENDAR.ERRORS.BLOCK';
      },
    });
  }

  private unblockDay(date: string) {
    if (this.selectedParkingId == null) {
      return;
    }
    this.errorMessage = '';
    this.blockedDays.delete(date);
    this.buildGrid();
    this.adminService.unblockDay(this.selectedParkingId, date).subscribe({
      error: (err) => {
        this.blockedDays.add(date);
        this.buildGrid();
        this.errorMessage = err.error?.error || 'ADMIN_CALENDAR.ERRORS.UNBLOCK';
      },
    });
  }

  closeDetail() {
    this.selectedDay = null;
    this.selectedDayBookings = [];
  }

  prevMonth() {
    if (this.month === 1) {
      this.month = 12;
      this.year -= 1;
    } else {
      this.month -= 1;
    }
    this.closeDetail();
    this.loadCalendar();
  }

  nextMonth() {
    if (this.month === 12) {
      this.month = 1;
      this.year += 1;
    } else {
      this.month += 1;
    }
    this.closeDetail();
    this.loadCalendar();
  }

  statusLabel(status: string): string {
    return status === '1' ? 'HISTORY.CONFIRMED' : 'HISTORY.CANCELLED';
  }

  private parseDate(value: string): Date {
    const [y, m, d] = value.slice(0, 10).split('-').map(Number);
    return new Date(y, m - 1, d);
  }

  private formatDate(date: Date): string {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  }
}
