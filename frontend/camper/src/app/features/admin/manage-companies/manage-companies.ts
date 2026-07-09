import { Component, ElementRef, OnDestroy, OnInit, ViewChild, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { Admin } from '../../../core/services/admin';
import { Auth } from '../../../core/services/auth';
import { Parking } from '../../../core/models/parking';
import { Company } from '../../../core/models/user';
import { ConfirmDialog } from '../../../shared/components/confirm-dialog/confirm-dialog';
import { CustomValidators } from '../../../shared/validators/custom-validators/custom-validators';
import { Chat } from '../../../core/services/chat';
import { ChatSocket } from '../../../core/services/chat-socket';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-manage-companies',
  imports: [CommonModule, ReactiveFormsModule, RouterLink, TranslateModule, ConfirmDialog],
  templateUrl: './manage-companies.html',
  styleUrl: './manage-companies.scss',
})
export class ManageCompanies implements OnInit, OnDestroy {
  @ViewChild('companyListScroll') companyListScroll?: ElementRef<HTMLElement>;
  @ViewChild('adsListScroll') adsListScroll?: ElementRef<HTMLElement>;

  private fb = inject(FormBuilder);
  private adminService = inject(Admin);
  private authService = inject(Auth);
  private chatService = inject(Chat);
  private chatSocket = inject(ChatSocket);
  private router = inject(Router);

  readonly pageSize = 8;
  readonly adsPageSize = 8;
  currentPage = 1;
  adsCurrentPage = 1;
  companies: Company[] = [];
  adsParkings: Parking[] = [];
  selectedCompanyId: number | null = null;
  isLoading = true;
  adsLoading = false;
  showForm = false;
  showAdsPanel = false;
  adsErrorMessage = '';
  successMessage = '';
  errorMessage = '';
  formErrorMessage = '';
  userName = '';
  unreadCount = 0;
  showDeleteConfirm = false;
  deleteConfirmParams: Record<string, string> = {};
  private companyPendingDelete: Company | null = null;
  private unreadSub?: Subscription;

  readonly maxFieldLength = 35;

  companyForm: FormGroup = this.fb.group({
    name: ['', [Validators.required, Validators.maxLength(this.maxFieldLength)]],
    cif: ['', [CustomValidators.cifValido]],
    adminEmail: ['', [Validators.required, Validators.email]],
    adminPassword: ['', [Validators.required, Validators.minLength(6)]],
    adminNombre: ['', [Validators.required, Validators.maxLength(this.maxFieldLength)]],
    adminApellidos: ['', [Validators.maxLength(this.maxFieldLength)]],
    adminDni: ['', [CustomValidators.dniValido]],
  });

  ngOnInit() {
    const user = this.authService.getUser();
    this.userName = user?.nombrePersona || user?.emailPersona || '';
    this.loadCompanies();
    this.loadUnreadCount();
    this.chatSocket.connect();
    this.unreadSub = this.chatSocket.onUnreadCount().subscribe((count) => {
      this.unreadCount = count;
    });
  }

  ngOnDestroy() {
    this.unreadSub?.unsubscribe();
  }

  loadUnreadCount() {
    this.chatService.getUnreadCount().subscribe({
      next: ({ count }) => {
        this.unreadCount = count;
      },
    });
  }

  get totalPages(): number {
    return Math.max(1, Math.ceil(this.companies.length / this.pageSize));
  }

  get paginatedCompanies(): Company[] {
    const start = (this.currentPage - 1) * this.pageSize;
    return this.companies.slice(start, start + this.pageSize);
  }

  get pageRangeStart(): number {
    if (this.companies.length === 0) {
      return 0;
    }
    return (this.currentPage - 1) * this.pageSize + 1;
  }

  get pageRangeEnd(): number {
    return Math.min(this.currentPage * this.pageSize, this.companies.length);
  }

  get adsTotalPages(): number {
    return Math.max(1, Math.ceil(this.adsParkings.length / this.adsPageSize));
  }

  get paginatedAds(): Parking[] {
    const start = (this.adsCurrentPage - 1) * this.adsPageSize;
    return this.adsParkings.slice(start, start + this.adsPageSize);
  }

  get adsPageRangeStart(): number {
    if (this.adsParkings.length === 0) {
      return 0;
    }
    return (this.adsCurrentPage - 1) * this.adsPageSize + 1;
  }

  get adsPageRangeEnd(): number {
    return Math.min(this.adsCurrentPage * this.adsPageSize, this.adsParkings.length);
  }

  get selectedCompanyName(): string {
    return this.companies.find((c) => c.id === this.selectedCompanyId)?.name || '';
  }

  loadCompanies() {
    this.isLoading = true;
    this.adminService.getCompanies().subscribe({
      next: (companies) => {
        this.companies = companies;
        this.clampCurrentPage();
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'ADMIN_COMPANIES.ERRORS.LOAD';
        this.isLoading = false;
      },
    });
  }

  toggleForm() {
    this.showForm = !this.showForm;
    this.errorMessage = '';
    this.formErrorMessage = '';
    this.successMessage = '';
    if (this.showForm) {
      this.showAdsPanel = false;
    }
    if (!this.showForm) {
      this.companyForm.reset();
    }
  }

  toggleAdsPanel() {
    this.showAdsPanel = !this.showAdsPanel;
    this.errorMessage = '';
    this.successMessage = '';
    if (this.showAdsPanel) {
      this.showForm = false;
      this.resetAdsState();
    }
  }

  onAdsCompanyChange(rawValue: string) {
    const companyId = rawValue ? Number(rawValue) : null;
    this.selectedCompanyId = companyId;
    this.adsCurrentPage = 1;
    this.adsErrorMessage = '';

    if (!companyId) {
      this.adsParkings = [];
      return;
    }

    this.loadCompanyAds(companyId);
  }

  loadCompanyAds(companyId: number) {
    this.adsLoading = true;
    this.adsErrorMessage = '';

    this.adminService.getParkings(companyId).subscribe({
      next: (parkings) => {
        this.adsParkings = parkings;
        this.clampAdsCurrentPage();
        this.adsLoading = false;
      },
      error: () => {
        this.adsErrorMessage = 'ADMIN_COMPANIES.ERRORS.LOAD_ADS';
        this.adsParkings = [];
        this.adsLoading = false;
      },
    });
  }

  openManageParking(parking: Parking) {
    if (!this.selectedCompanyId) {
      return;
    }

    this.router.navigate(['/admin/parking', parking.id], {
      queryParams: { companyId: this.selectedCompanyId },
    });
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

  createCompany() {
    if (this.companyForm.invalid) {
      this.companyForm.markAllAsTouched();
      this.formErrorMessage = 'ADMIN_COMPANIES.ERRORS.VALIDATION';
      return;
    }

    this.formErrorMessage = '';
    this.adminService.createCompany(this.companyForm.value).subscribe({
      next: () => {
        this.successMessage = 'ADMIN_COMPANIES.SUCCESS_CREATE';
        this.companyForm.reset();
        this.showForm = false;
        this.loadCompanies();
      },
      error: (err) => {
        this.errorMessage = err.error?.error || 'ADMIN_COMPANIES.ERRORS.CREATE';
      },
    });
  }

  openCompanyParkings(company: Company) {
    this.router.navigate(['/admin/companies', company.id, 'parkings']);
  }

  editCompany(event: Event, company: Company) {
    event.stopPropagation();
    this.router.navigate(['/admin/companies', company.id, 'edit']);
  }

  deleteCompany(event: Event, company: Company) {
    event.stopPropagation();
    this.companyPendingDelete = company;
    this.deleteConfirmParams = { name: company.name };
    this.showDeleteConfirm = true;
  }

  cancelDeleteCompany() {
    this.showDeleteConfirm = false;
    this.companyPendingDelete = null;
  }

  confirmDeleteCompany() {
    const company = this.companyPendingDelete;
    if (!company) {
      return;
    }

    this.showDeleteConfirm = false;
    this.companyPendingDelete = null;

    this.adminService.deleteCompany(company.id).subscribe({
      next: () => {
        this.successMessage = 'ADMIN_COMPANIES.SUCCESS_DELETE';
        this.loadCompanies();
      },
      error: (err) => {
        this.errorMessage = err.error?.error || 'ADMIN_COMPANIES.ERRORS.DELETE';
      },
    });
  }

  adminDisplayName(company: Company): string {
    return [company.adminName, company.adminApellidos].filter(Boolean).join(' ').trim();
  }

  goToPage(page: number) {
    if (page < 1 || page > this.totalPages || page === this.currentPage) {
      return;
    }
    this.currentPage = page;
    this.scrollListToTop();
  }

  prevPage() {
    this.goToPage(this.currentPage - 1);
  }

  nextPage() {
    this.goToPage(this.currentPage + 1);
  }

  private clampCurrentPage() {
    if (this.currentPage > this.totalPages) {
      this.currentPage = this.totalPages;
    }
  }

  private clampAdsCurrentPage() {
    if (this.adsCurrentPage > this.adsTotalPages) {
      this.adsCurrentPage = this.adsTotalPages;
    }
  }

  private resetAdsState() {
    this.selectedCompanyId = null;
    this.adsParkings = [];
    this.adsCurrentPage = 1;
    this.adsLoading = false;
    this.adsErrorMessage = '';
  }

  private scrollListToTop() {
    this.companyListScroll?.nativeElement.scrollTo({ top: 0, behavior: 'smooth' });
  }

  logout() {
    this.authService.logoutAdmin();
  }

  isFieldInvalid(field: string): boolean {
    const control = this.companyForm.get(field);
    return !!(control && control.invalid && control.touched);
  }
}
