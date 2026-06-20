import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { Admin } from '../../../core/services/admin';
import { AdminUser, Company } from '../../../core/models/user';

@Component({
  selector: 'app-manage-company-detail',
  imports: [CommonModule, ReactiveFormsModule, RouterLink, TranslateModule],
  templateUrl: './manage-company-detail.html',
  styleUrl: './manage-company-detail.scss',
})
export class ManageCompanyDetail implements OnInit {
  private fb = inject(FormBuilder);
  private adminService = inject(Admin);
  private route = inject(ActivatedRoute);

  companyId!: number;
  company: Company | null = null;
  users: AdminUser[] = [];
  isLoading = true;
  successMessage = '';
  errorMessage = '';

  editingUserId: number | null = null;

  companyForm: FormGroup = this.fb.group({
    name: ['', Validators.required],
    cif: [''],
  });

  adminForm: FormGroup = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: [''],
    nombre: ['', Validators.required],
    apellidos: [''],
    dni: [''],
  });

  userForm: FormGroup = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: [''],
    nombre: ['', Validators.required],
    apellidos: [''],
    dni: [''],
    role: ['user', Validators.required],
  });

  ngOnInit() {
    this.companyId = Number(this.route.snapshot.paramMap.get('id'));
    this.loadData();
  }

  loadData() {
    this.isLoading = true;
    this.adminService.getCompany(this.companyId).subscribe({
      next: (company) => {
        this.company = company;
        this.companyForm.patchValue({ name: company.name, cif: company.cif || '' });
        if (company.adminUserId) {
          this.adminForm.patchValue({
            email: company.adminEmail || '',
            nombre: company.adminName || '',
            apellidos: company.adminApellidos || '',
            dni: company.adminDni || '',
          });
        }
      },
      error: () => {
        this.errorMessage = 'ADMIN_COMPANIES.ERRORS.LOAD';
        this.isLoading = false;
      },
    });

    this.adminService.getCompanyUsers(this.companyId).subscribe({
      next: (users) => {
        this.users = users;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      },
    });
  }

  saveCompany() {
    if (this.companyForm.invalid) {
      this.companyForm.markAllAsTouched();
      return;
    }

    this.adminService.updateCompany(this.companyId, this.companyForm.value).subscribe({
      next: (company) => {
        this.company = company;
        this.successMessage = 'ADMIN_COMPANIES.SUCCESS_UPDATE';
        this.clearSuccessLater();
      },
      error: (err) => {
        this.errorMessage = err.error?.error || 'ADMIN_COMPANIES.ERRORS.UPDATE';
      },
    });
  }

  saveAdmin() {
    if (!this.company?.adminUserId || this.adminForm.invalid) {
      this.adminForm.markAllAsTouched();
      return;
    }

    const data = { ...this.adminForm.value, role: 'admin', companyId: this.companyId };
    if (!data.password) {
      delete data.password;
    }

    this.adminService.updateUser(this.company.adminUserId, data).subscribe({
      next: () => {
        this.adminForm.patchValue({ password: '' });
        this.successMessage = 'ADMIN_COMPANIES.SUCCESS_ADMIN_UPDATE';
        this.loadData();
        this.clearSuccessLater();
      },
      error: (err) => {
        this.errorMessage = err.error?.error || 'ADMIN_COMPANIES.ERRORS.ADMIN_UPDATE';
      },
    });
  }

  startEditUser(user: AdminUser) {
    this.editingUserId = user.id;
    this.userForm.patchValue({
      email: user.email,
      password: '',
      nombre: user.nombre,
      apellidos: user.apellidos,
      dni: user.dni,
      role: user.role,
    });
  }

  cancelEditUser() {
    this.editingUserId = null;
    this.userForm.reset({ role: 'user' });
  }

  saveUser() {
    if (!this.editingUserId || this.userForm.invalid) {
      this.userForm.markAllAsTouched();
      return;
    }

    const data = { ...this.userForm.value, companyId: this.companyId };
    if (!data.password) {
      delete data.password;
    }

    this.adminService.updateUser(this.editingUserId, data).subscribe({
      next: () => {
        this.cancelEditUser();
        this.successMessage = 'ADMIN_COMPANIES.SUCCESS_USER_UPDATE';
        this.loadData();
        this.clearSuccessLater();
      },
      error: (err) => {
        this.errorMessage = err.error?.error || 'ADMIN_COMPANIES.ERRORS.USER_UPDATE';
      },
    });
  }

  roleLabel(role: string): string {
    if (role === 'admin') return 'ADMIN_USERS.ROLE_ADMIN';
    if (role === 'super_admin') return 'ADMIN_USERS.ROLE_SUPER';
    return 'ADMIN_USERS.ROLE_USER';
  }

  private clearSuccessLater() {
    setTimeout(() => {
      this.successMessage = '';
    }, 3000);
  }
}
