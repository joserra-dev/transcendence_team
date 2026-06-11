import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { ParkingService } from '../../../core/services/parking';
import { Parking, Plaza, SearchFilters } from '../../../core/models/parking';
import { FormsModule } from '@angular/forms';
import { Auth } from '../../../core/services/auth';
import { BookingService } from '../../../core/services/booking';
import { BookingRequest } from '../../../core/models/booking';

@Component({
  selector: 'app-parking-detail',
  standalone: true,
  imports: [CommonModule, TranslateModule, FormsModule],
  templateUrl: './parking-detail.html',
  styleUrls: ['./parking-detail.scss']
})
export class ParkingDetail implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private parkingService = inject(ParkingService);
  private authService = inject(Auth);
  private bookingService = inject(BookingService);

  parking: Parking | null = null;
  selectedSpot: Plaza | null = null;
  isLoading = true;

  errorMessage = '';
  successMessage = '';
  showConfirmModal = false;

  isMobile = false;

  entryDate: string = '';
  exitDate: string = '';
  licensePlate: string = '';

  ngOnInit() {
    this.checkViewport();

    window.addEventListener('resize', () => {
      this.checkViewport();
    });

    const parkingId = this.route.snapshot.paramMap.get('id');
    this.route.queryParams.subscribe(params => {
      const today = new Date();
      const tomorrow = new Date(today);
      tomorrow.setDate(tomorrow.getDate() + 1);

      this.entryDate = params['fechaDesde'] || today.toISOString().split('T')[0];
      this.exitDate = params['fechaHasta'] || tomorrow.toISOString().split('T')[0];
    });
    if (parkingId) {
      this.loadParkingDetails(parkingId);
    }
  }

  loadParkingDetails(id: string) {
    this.isLoading = true;
    this.errorMessage = '';
    const filters: SearchFilters = {
      id: Number(id),
      fechaDesde: this.entryDate,
      fechaHasta: this.exitDate
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
        this.errorMessage = 'PARKING.ERRORS.LOADING';
        this.isLoading = false;
      }
    });
  }

  get spots(): Plaza[] {
    return this.parking?.plazasResponse || this.parking?.plazas || [];
  }

  get totalPrice(): number {
    if (!this.selectedSpot || !this.entryDate || !this.exitDate) return 0;

    const start = new Date(this.entryDate);
    const end = new Date(this.exitDate);

    const diffTime = Math.abs(end.getTime() - start.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return (diffDays+1) * this.selectedSpot.precio;
  }

  selectSpot(spot: Plaza) {
    if (spot.estado !== '0') return;
    this.selectedSpot = spot;
  }

  onBook() {
    if (!this.selectedSpot) return;

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
        console.error(err);
        this.errorMessage = 'PARKING.ERRORS.BOOKING';
        this.isLoading = false;
      }
    });
  }

  // Para la galería
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
    this.currentImage =
      (this.currentImage + 1) % this.galleryImages.length;
  }

  prevImage(event: Event) {
    event.stopPropagation();
    this.currentImage =
      (this.currentImage - 1 + this.galleryImages.length) %
      this.galleryImages.length;
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
  if (!this.licensePlate) {
    return false;
  }
  
  // 1. Limpieza total: quitamos espacios, guiones, barras, puntos y pasamos a mayúsculas
  const cleanedPlate = this.licensePlate.replace(/[\s\-_.]/g, '').toUpperCase();
  
  // 2. Patrón internacional: alfanumérico de entre 3 y 15 caracteres
  const globalPlateRegex = /^[A-Z0-9]{3,15}$/;
  
  // 3. Devolvemos el resultado de la validación
  return globalPlateRegex.test(cleanedPlate);
}

  // Para detectar el movil
  checkViewport() {
    this.isMobile = window.innerWidth <= 768;
  }
}
