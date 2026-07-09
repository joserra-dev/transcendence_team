import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';

import { ParkingService } from '../../../core/services/parking';
import { BookingService } from '../../../core/services/booking';
import { Auth } from '../../../core/services/auth';
import { Parking, Space, SearchFilters, ParkingPage } from '../../../core/models/parking';
import { BookingRequest } from '../../../core/models/booking';

@Component({
  selector: 'app-parking-detail',
  standalone: true,
  imports: [CommonModule, TranslateModule, FormsModule],
  templateUrl: './parking-detail.html',
  styleUrls: ['./parking-detail.scss']
})
export class ParkingDetail implements OnInit, OnDestroy {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private parkingService = inject(ParkingService);
  private authService = inject(Auth);
  private bookingService = inject(BookingService);
  private translate = inject(TranslateService);
  private sanitizer = inject(DomSanitizer);

  parking: Parking | null = null;
  selectedSpot: Space | null = null;
  isLoading = true;

  errorMessage = '';
  successMessage = '';
  spamMessage = '';
  showConfirmModal = false;
  showMapModal = false;

  isMobile = false;

  entryDate: string = '';
  exitDate: string = '';
  licensePlate: string = '';

  dateFormat: string = 'dd/MM/yyyy';
  mapUrl: SafeResourceUrl | null = null;
  private langFormatSub!: Subscription;

  ngOnInit() {
    this.checkViewport();

    window.addEventListener('resize', () => {
      this.checkViewport();
    });

    this.langFormatSub = this.translate.onLangChange.subscribe((event) => {
      this.dateformatdefine(event.lang);
    });

    this.dateformatdefine(this.translate.currentLang || this.translate.defaultLang || 'es');

    const parkingId = this.route.snapshot.paramMap.get('id');
    this.route.queryParams.subscribe(params => {
      const today = new Date();
      const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);
      const tomorrowStr = `${tomorrow.getFullYear()}-${String(tomorrow.getMonth() + 1).padStart(2, '0')}-${String(tomorrow.getDate()).padStart(2, '0')}`;

      this.entryDate = params['startDate'] || todayStr;
      this.exitDate = params['endDate'] || tomorrowStr;
    });

    if (parkingId) {
      this.loadParkingDetails(parkingId);
    }
  }

  private dateformatdefine(lang: string) {
    const idioma = lang.toLowerCase();
    if (idioma === 'eu' || idioma === 'en') {
      this.dateFormat = 'yyyy/MM/dd';
    } else {
      this.dateFormat = 'dd/MM/yyyy';
    }
  }

  loadParkingDetails(id: string) {
    this.isLoading = true;
    this.errorMessage = '';
    const filters: SearchFilters = {
      id: Number(id),
      startDate: this.entryDate,
      endDate: this.exitDate
    };
    this.parkingService.searchParkings(filters).subscribe({
      next: (data) => {
        if (data && data.items && data.items.length > 0) {
          this.parking = data.items[0];
        } else {
          this.errorMessage = 'PARKING.ERRORS.NOT_FOUND';
        }
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = 'PARKING.ERRORS.LOADING';
        this.isLoading = false;
      }
    });
  }

  get spots(): Space[] {
    return this.parking?.plazasResponse || this.parking?.spaces || [];
  }

  get totalPrice(): number {
    if (!this.selectedSpot || !this.entryDate || !this.exitDate || !this.isDateRangeValid()) return 0;

    const start = new Date(this.entryDate);
    const end = new Date(this.exitDate);

    const diffTime = end.getTime() - start.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays * this.selectedSpot.price;
  }

  isDateRangeValid(): boolean {
    if (!this.entryDate || !this.exitDate) return false;

    const start = new Date(this.entryDate);
    const expectedExit = new Date(start);
    expectedExit.setDate(expectedExit.getDate() + 1);
    const end = new Date(this.exitDate);

    return end >= expectedExit;
  }

  selectSpot(spot: Space) {
    this.selectedSpot = spot;
  }

  onBook() {
    if (!this.selectedSpot) return;

    if (!this.isDateRangeValid()) {
      this.errorMessage = 'PARKING.ERRORS.INVALID_DATES';
      this.successMessage = '';
      this.showConfirmModal = false;
      return;
    }

    this.errorMessage = '';

    if (!this.authService.isLoggedIn()) {
      this.router.navigate(['/auth/login-client'], {
        queryParams: { returnUrl: this.router.url }
      });
      return;
    }

    this.showConfirmModal = true;
  }

  /**
   * Envía la reserva al backend (Flask /api/booking) e inicia la redirección a Stripe
   */
  confirmBooking() {
    if (!this.selectedSpot || !this.parking) return;

    if (!this.isDateRangeValid() || !this.isLicensePlateValid()) {
      this.errorMessage = 'PARKING.ERRORS.INVALID_DATES';
      this.successMessage = '';
      this.isLoading = false;
      this.showConfirmModal = false;
      return;
    }

    this.showConfirmModal = false;
    this.isLoading = true;

      const bookingPayload = {
      idSpace: this.selectedSpot.id,
      idParking: this.parking.id,
      startDate: this.entryDate,
      endDate: this.exitDate,
      licensePlate: this.licensePlate.replace(/[\s\-_.]/g, '').toUpperCase()
    };

    // Llamamos a tu servicio mapeado correctamente a /api/booking
    this.bookingService.createBooking(bookingPayload).subscribe({
      next: (res: any) => {
        // Al quitar responseType: 'text', 'res' ya es un objeto JSON parsed por Angular
        if (res && res.url) {
          //Redirección a la pasarela segura de Stripe Checkout
          window.location.href = res.url;
        } else {
          this.errorMessage = 'No se recibió la URL de pago desde el servidor.';
          this.isLoading = false;
        }
      },
      error: (err) => {
        console.error("Error al procesar la reserva en Flask:", err);
        this.errorMessage = 'PARKING.ERRORS.BOOKING';
        this.isLoading = false;
      }
    });
  }

  openMapModal() {
    if (!this.parking || !this.parking.latitude || !this.parking.longitude) return;
    const lat = this.parking.latitude;
    const lon = this.parking.longitude;
    
    const rawUrl = `https://maps.google.com/maps?q=${lat},${lon}&z=15&output=embed&t=m`;
    this.mapUrl = this.sanitizer.bypassSecurityTrustResourceUrl(rawUrl);
    this.showMapModal = true;
  }

  closeMapModal() {
    this.showMapModal = false;
    this.mapUrl = null;
  }

  // Galerías de imágenes
  galleryImages: string[] = [
    '/images/fotos/camper1.jpg',
    '/images/fotos/camper2.jpg',
    '/images/fotos/camper3.jpg',
    '/images/fotos/camper4.jpg',
    '/images/fotos/camper5.jpg'
  ];

  isGalleryOpen = false;
  currentImage = 1;

  get sideGalleryImages(): string[] {
    return this.galleryImages.slice(1);
  }

  openGallery(index: number) {
    this.currentImage = index;
    this.isGalleryOpen = true;
  }

  closeGallery() {
    this.isGalleryOpen = false;
  }

  nextImage(event: Event) {
    event.stopPropagation();
    this.currentImage = (this.currentImage + 1) % this.galleryImages.length;
  }

  prevImage(event: Event) {
    event.stopPropagation();
    this.currentImage = (this.currentImage - 1 + this.galleryImages.length) % this.galleryImages.length;
  }

  isLicensePlateValid(): boolean {
    if (!this.licensePlate) return false;
    const cleanedPlate = this.licensePlate.replace(/[\s\-_.]/g, '').toUpperCase();
    const globalPlateRegex = /^[A-Z0-9]{3,15}$/;
    return globalPlateRegex.test(cleanedPlate);
  }

  checkViewport() {
    this.isMobile = window.innerWidth <= 768;
  }

  ngOnDestroy() {
    if (this.langFormatSub) {
      this.langFormatSub.unsubscribe();
    }
  }
}