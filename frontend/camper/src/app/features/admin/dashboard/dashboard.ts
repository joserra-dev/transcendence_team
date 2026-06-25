import { Component, ElementRef, OnInit, ViewChild, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { Admin } from '../../../core/services/admin';
import { Auth } from '../../../core/services/auth';
import { Parking } from '../../../core/models/parking';

@Component({
  selector: 'app-dashboard',
  imports: [RouterLink, CommonModule, TranslateModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard implements OnInit {
  @ViewChild('adsListScroll') adsListScroll?: ElementRef<HTMLElement>;

  private adminService = inject(Admin);
  private authService = inject(Auth);
  private router = inject(Router);

  readonly adsPageSize = 8;

  parkings: Parking[] = [];
  adsCurrentPage = 1;
  isLoading = true;
  errorMessage = '';
  userName = '';

  ngOnInit() {
    const user = this.authService.getUser();
    this.userName = user?.nombrePersona || user?.emailPersona || '';
    this.loadParkings();
  }

  get adsTotalPages(): number {
    return Math.max(1, Math.ceil(this.parkings.length / this.adsPageSize));
  }

  get paginatedAds(): Parking[] {
    const start = (this.adsCurrentPage - 1) * this.adsPageSize;
    return this.parkings.slice(start, start + this.adsPageSize);
  }

  get adsPageRangeStart(): number {
    if (this.parkings.length === 0) {
      return 0;
    }
    return (this.adsCurrentPage - 1) * this.adsPageSize + 1;
  }

  get adsPageRangeEnd(): number {
    return Math.min(this.adsCurrentPage * this.adsPageSize, this.parkings.length);
  }

  loadParkings() {
    this.isLoading = true;
    this.errorMessage = '';

    this.adminService.getParkings().subscribe({
      next: (data) => {
        this.parkings = data;
        this.clampAdsCurrentPage();
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'ADMIN_DASHBOARD.ERRORS.LOAD_ADS';
        this.isLoading = false;
      },
    });
  }

  openManageParking(parking: Parking) {
    this.router.navigate(['/admin/parking', parking.id]);
  }

  goToAdsPage(page: number) {
    if (page < 1 || page > this.adsTotalPages || page === this.adsCurrentPage) {
      return;
    }
    this.adsCurrentPage = page;
    this.adsListScroll?.nativeElement.scrollTo({ top: 0, behavior: 'smooth' });
  }

  prevAdsPage() {
    this.goToAdsPage(this.adsCurrentPage - 1);
  }

  nextAdsPage() {
    this.goToAdsPage(this.adsCurrentPage + 1);
  }

  logout() {
    this.authService.logoutAdmin();
  }

  private clampAdsCurrentPage() {
    if (this.adsCurrentPage > this.adsTotalPages) {
      this.adsCurrentPage = this.adsTotalPages;
    }
  }
}
