import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { BookingService } from '../../../core/services/booking';
import { Booking } from '../../../core/models/booking';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-booking-detail',
  standalone: true,
  imports: [CommonModule, TranslateModule, FormsModule],
  templateUrl: './booking-detail.html',
  styleUrls: ['./booking-detail.scss']
})
export class BookingDetail implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private bookingService = inject(BookingService);
  private translate = inject(TranslateService);

  booking: any | null = null;
  isLoading = true;
  today = new Date().toISOString().slice(0, 10);

  errorMessage = '';
  successMessage = '';

  showlPlateModal = false;
  licensePlate: string | null = null;

  showRateModal = false;
  rateValue = 5;

  showCancelModal = false;

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadBooking(id);
    } else {
      this.router.navigate(['/client/history']);
    }
  }

  loadBooking(id: string) {
    this.isLoading = true;

    this.bookingService.getBookingById(id).subscribe({
      next: (data) => {
        this.booking = data;
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = 'HISTORY_DETAIL.ERRORS.LOADING';
        this.isLoading = false;
      }
    });
  }

  cancelBooking() {
    if (!this.booking) return;
      this.showCancelModal = true;
    }

  confirmCancellation() {
    this.showCancelModal = false;
    this.isLoading = true;
    this.bookingService.cancelBooking(this.booking.id).subscribe({
      next: (response: any) => {
        this.handleCancelSuccess();
      },
      error: (err) => {
        if (err.status === 200) {
           this.handleCancelSuccess();
        } else {
           this.handleError(err, 'HISTORY_DETAIL.ERRORS.CANCEL');
            this.isLoading = false;
        }
      }
    });
  }

  retryPayment() {
    if (!this.booking) return;
    this.isLoading = true;
    this.bookingService.retryPayment(this.booking.id).subscribe({
      next: (res: any) => {
        this.isLoading = false;
        if (res && res.url) {
          window.location.href = res.url;
        }
      },
      error: (err) => {
        this.isLoading = false;
        this.handleError(err, 'HISTORY_DETAIL.ERRORS.RETRY');
      }
    });
  }

  private handleCancelSuccess() {
    this.showSuccess('HISTORY_DETAIL.SUCCESS_CANCEL');
    if (this.booking) {
      this.booking.status = '0';
    }
    this.loadBooking(this.booking.id);
  }

  viewLicensePlate() {
    if (!this.booking) return;
    this.showlPlateModal = true;
  }

  rateBooking() {
    this.rateValue = 5;
    this.showRateModal = true;
  }

  confirmRating() {
    if (!this.booking) return;

    this.isLoading = true;
    this.showRateModal = false;

    this.bookingService.rateBooking(this.booking.id, this.rateValue).subscribe({
      next: (response: any) => {
        this.showSuccess('HISTORY_DETAIL.SUCCESS_RATE');
        this.loadBooking(this.booking.id);
      },
      error: (err) => {
        if (err.status === 200) {
           this.showSuccess('HISTORY_DETAIL.SUCCESS_RATE');
           this.loadBooking(this.booking.id);
        } else {
           this.handleError(err, 'HISTORY_DETAIL.ERRORS.RATE');
           this.isLoading = false;
        }
      }
    });
  }

  closePlateModal() {
    this.showlPlateModal = false;
    this.licensePlate = null;
  }

  goBack() {
    this.router.navigate(['/client/history']);
  }

  private showSuccess(msg: string) {
    this.successMessage = this.translate.instant(msg);
    setTimeout(() => {
        this.successMessage = '';
    }, 3000);
  }

  private handleError(err: any, defaultMsg: string, isQr = false) {
    let errorMsg = this.translate.instant(defaultMsg);

    if (isQr && err.status === 400) {
       errorMsg = 'Error: No se encontró la reserva o no tienes permiso para ver este QR.';
    }

    if (err.error) {
       if (typeof err.error === 'string') {
         errorMsg = err.error;
       } else if (err.error.error) {
         errorMsg = err.error.error;
       } else if (err.error.message) {
         errorMsg = err.error.message;
       }
    }
    this.errorMessage = errorMsg;
  }

  getStatusLabel(status: string): string {
    if (status === '1') return 'HISTORY_DETAIL.CONFIRMED';
    if (status === '2') return 'HISTORY_DETAIL.PROCESSING';
    return 'HISTORY_DETAIL.CANCELLED';
  }

  send_bill() {
    this.isLoading = true;

    this.bookingService.send_bill(this.booking.id).subscribe({
      next: (data) => {
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = 'HISTORY_DETAIL.ERRORS.LOADING';
        this.isLoading = false;
      }
    });
  }
}
