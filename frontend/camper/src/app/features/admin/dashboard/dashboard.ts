import { Component, ElementRef, OnInit, ViewChild, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { Admin } from '../../../core/services/admin';
import { Auth } from '../../../core/services/auth';
import { Parking } from '../../../core/models/parking';

@Component({
  selector: 'app-dashboard',
  imports: [RouterLink, CommonModule, FormsModule, TranslateModule],
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
  filterStatus: 'all' | 'active' | 'inactive' = 'all';
  filterMunicipality: string | 'all' = 'all';
  sortOrder: 'asc' | 'desc' = 'asc';

  ngOnInit() {
    const user = this.authService.getUser();
    this.userName = user?.nombrePersona || user?.emailPersona || '';
    this.loadParkings();
  }

  get adsTotalPages(): number {
    return Math.max(1, Math.ceil(this.filteredParkings.length / this.adsPageSize));
  }

  get filteredParkings(): Parking[] {
    let result = [...this.parkings];

    if (this.filterStatus === 'active') {
      result = result.filter((parking) => parking.isActive !== false);
    } else if (this.filterStatus === 'inactive') {
      result = result.filter((parking) => parking.isActive === false);
    }

    if (this.filterMunicipality !== 'all') {
      result = result.filter(
        (parking) => (parking.localidad || parking.municipality || '') === this.filterMunicipality
      );
    }

    result.sort((a, b) => {
      const cmp = a.name.localeCompare(b.name, 'es', { sensitivity: 'base' });
      return this.sortOrder === 'asc' ? cmp : -cmp;
    });

    return result;
  }

  get municipalityOptions(): string[] {
    const values = this.parkings
      .map((parking) => parking.localidad || parking.municipality || '')
      .filter(Boolean);
    return [...new Set(values)].sort((a, b) => a.localeCompare(b, 'es', { sensitivity: 'base' }));
  }

  get paginatedAds(): Parking[] {
    const start = (this.adsCurrentPage - 1) * this.adsPageSize;
    return this.filteredParkings.slice(start, start + this.adsPageSize);
  }

  get adsPageRangeStart(): number {
    if (this.filteredParkings.length === 0) {
      return 0;
    }
    return (this.adsCurrentPage - 1) * this.adsPageSize + 1;
  }

  get adsPageRangeEnd(): number {
    return Math.min(this.adsCurrentPage * this.adsPageSize, this.filteredParkings.length);
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

  onFiltersChange() {
    this.adsCurrentPage = 1;
    this.clampAdsCurrentPage();
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
