import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router } from '@angular/router';
import { ActivatedRoute } from '@angular/router';
import { Title } from '@angular/platform-browser';
import { BookingService } from '../../../core/services/booking';
import { TranslateModule, TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-booking-cancelled',
  standalone: true,
  imports: [CommonModule, RouterLink, TranslateModule],
  templateUrl: './booking-cancelled.html',
  styleUrls: ['./booking-cancelled.scss']
})
export class BookingCancelled implements OnInit {
  private route = inject(ActivatedRoute);
  private titleService = inject(Title);
  private bookingService = inject(BookingService);
  private router = inject(Router);
  private translate = inject(TranslateService);

  bookingId: number = 0;
  booking: any | null = null;
  isLoading = true;
  fromStripe = false;

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    this.fromStripe = this.route.snapshot.queryParamMap.get('from') === 'stripe';
    if (id) {
      this.bookingId = Number(id);
      this.bookingService.getBookingById(this.bookingId).subscribe({
        next: (data) => {
          this.booking = data;
          this.isLoading = false;
          this.updateTitle();
        },
        error: () => {
          this.isLoading = false;
        }
      });
    } else {
      this.isLoading = false;
    }
  }

  private updateTitle() {
    const key = this.fromStripe ? 'HISTORY_DETAIL.PENDING_TITLE' : 'HISTORY_DETAIL.CANCELLED_TITLE';
    this.titleService.setTitle(this.translate.instant(key));
  }

  newBooking() {
    this.router.navigate(['/client/history']);
  }
}