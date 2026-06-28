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
import { Parking, Space, SearchFilters } from '../../../core/models/parking';
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
        if (data && data.length > 0) {
          this.parking = data[0];
        } else {
          this.errorMessage = 'PARKING.ERRORS.NOT_FOUND';
        }
        this.isLoading = false;
      },
      error: (err) => {
        console.error(err);
        if (err.status === 404) {
          this.errorMessage = 'PARKING.ERRORS.NOT_FOUND';
        } else {
          this.errorMessage = 'PARKING.ERRORS.LOADING';
        }
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

    const user = this.authService.getUser();
    const hasIban = (user?.metodoPago === 'iban' || !user?.metodoPago) && user?.ibanPersona;
    const hasCard = user?.metodoPago === 'tarjeta' && user?.tarjeta;
    const hasCash = user?.metodoPago === 'efectivo';

    if (!hasIban && !hasCard && !hasCash) {
      this.router.navigate(['/client/profile']);
      return;
    }
    this.showConfirmModal = true;
  }

  confirmBooking() {
    if (!this.selectedSpot || !this.parking) return;

    if (!this.isDateRangeValid()) {
      this.errorMessage = 'PARKING.ERRORS.INVALID_DATES';
      this.successMessage = '';
      this.isLoading = false;
      this.showConfirmModal = false;
      return;
    }

    this.showConfirmModal = false;
    this.isLoading = true;
    const bookingData: BookingRequest = {
      idSpace: this.selectedSpot.id,
      idParking: this.parking!.id,
      startDate: this.entryDate,
      endDate: this.exitDate,
      licensePlate: this.licensePlate
    };

    this.bookingService.createBooking(bookingData).subscribe({
      next: (res) => {
        this.successMessage = 'PARKING.SUCCESS';
        this.router.navigate(['/client/history']);
      },
      error: (err) => {
        console.error("Booking Error Objeto Completo:", err);
        let errorMsg = 'PARKING.ERRORS.BOOKING';
        
        if (err.error) {
            if (typeof err.error === 'string') {
                try {
                    const parsed = JSON.parse(err.error);
                    errorMsg = parsed.error || parsed.message || err.error;
                } catch(e) {
                    errorMsg = err.error;
                }
            } else if (err.error.error) {
                errorMsg = err.error.error;
            } else if (err.error.message) {
                errorMsg = err.error.message;
            } else {
                try { errorMsg = JSON.stringify(err.error); } catch(e) {}
            }
        } else if (err.message) {
            errorMsg = err.message;
        }

        this.spamMessage = "🚨 AVISO 🚨\n\n" + errorMsg;
        this.errorMessage = errorMsg;
        this.isLoading = false;
      }
    });
  }

  openMapModal() {
    if (!this.parking || !this.parking.latitude || !this.parking.longitude) return;
    const lat = this.parking.latitude;
    const lon = this.parking.longitude;
    
    // 💡 URL configurada para Google Maps con marcador centrado (Zoom z=15)
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

  getPaymentMethodLabel(): string {
    const user = this.authService.getUser();
    if (!user) return '';
    const metodo = user.metodoPago || 'iban';
    if (metodo === 'iban' && user.ibanPersona) {
      const lastDigits = user.ibanPersona.slice(-4);
      return `Cuenta Bancaria (ES...${lastDigits})`;
    } else if (metodo === 'tarjeta' && user.tarjeta) {
      const lastDigits = user.tarjeta.slice(-4);
      return `Tarjeta de Crédito (**** **** **** ${lastDigits})`;
    } else if (metodo === 'efectivo') {
      return 'Pago en Efectivo (Se abonará al llegar)';
    }
    return '';
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