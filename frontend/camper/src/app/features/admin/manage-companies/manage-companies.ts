import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { Admin } from '../../../core/services/admin';
import { Auth } from '../../../core/services/auth';
import { Company } from '../../../core/models/user';

@Component({
  selector: 'app-manage-companies',
  imports: [CommonModule, ReactiveFormsModule, RouterLink, TranslateModule],
  templateUrl: './manage-companies.html',
  styleUrl: './manage-companies.scss',
})
export class ManageCompanies implements OnInit {
  private fb = inject(FormBuilder);
  private adminService = inject(Admin);
  private authService = inject(Auth);
  private router = inject(Router);
  private translate = inject(TranslateService);

  companies: Company[] = [];
  isLoading = true;
  showForm = false;
  successMessage = '';
  errorMessage = '';
  userName = '';

  companyForm: FormGroup = this.fb.group({
    name: ['', Validators.required],
    cif: [''],
    adminEmail: ['', [Validators.required, Validators.email]],
    adminPassword: ['', [Validators.required, Validators.minLength(6)]],
    adminNombre: ['', Validators.required],
    adminApellidos: [''],
    adminDni: [''],
  });

  ngOnInit() {
    const user = this.authService.getUser();
    this.userName = user?.nombrePersona || user?.emailPersona || '';
    this.loadCompanies();
  }

  loadCompanies() {
    this.isLoading = true;
    this.adminService.getCompanies().subscribe({
      next: (companies) => {
        this.companies = companies;
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
    this.successMessage = '';
    if (!this.showForm) {
      this.companyForm.reset();
    }
  }

  createCompany() {
    if (this.companyForm.invalid) {
      this.companyForm.markAllAsTouched();
      return;
    }

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
    const msg = this.translate.instant('ADMIN_COMPANIES.CONFIRM_DELETE', { name: company.name });
    if (!confirm(msg)) {
      return;
    }

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

  logout() {
    this.authService.logoutAdmin();
  }
}
