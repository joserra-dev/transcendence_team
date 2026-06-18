import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { Admin } from '../../../core/services/admin';
import { AdminUser, Company } from '../../../core/models/user';

@Component({
  selector: 'app-manage-users',
  imports: [CommonModule, ReactiveFormsModule, RouterLink, TranslateModule],
  templateUrl: './manage-users.html',
  styleUrl: './manage-users.scss',
})
export class ManageUsers implements OnInit {
  private fb = inject(FormBuilder);
  private adminService = inject(Admin);

  users: AdminUser[] = [];
  companies: Company[] = [];
  isLoading = true;
  showForm = false;
  successMessage = '';
  errorMessage = '';

  userForm: FormGroup = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]],
    nombre: ['', Validators.required],
    apellidos: [''],
    dni: [''],
    role: ['user', Validators.required],
    companyId: [null],
  });

  ngOnInit() {
    this.loadData();
    this.userForm.get('role')?.valueChanges.subscribe((role) => {
      const companyControl = this.userForm.get('companyId');
      if (role === 'admin') {
        companyControl?.setValidators([Validators.required]);
      } else {
        companyControl?.clearValidators();
        companyControl?.setValue(null);
      }
      companyControl?.updateValueAndValidity();
    });
  }

  loadData() {
    this.isLoading = true;
    this.adminService.getUsers().subscribe({
      next: (users) => {
        this.users = users;
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'ADMIN_USERS.ERRORS.LOAD';
        this.isLoading = false;
      },
    });

    this.adminService.getCompanies().subscribe({
      next: (companies) => (this.companies = companies),
    });
  }

  toggleForm() {
    this.showForm = !this.showForm;
    this.errorMessage = '';
    this.successMessage = '';
    if (!this.showForm) {
      this.userForm.reset({ role: 'user' });
    }
  }

  createUser() {
    if (this.userForm.invalid) {
      this.userForm.markAllAsTouched();
      return;
    }

    this.adminService.createUser(this.userForm.value).subscribe({
      next: () => {
        this.successMessage = 'ADMIN_USERS.SUCCESS_CREATE';
        this.userForm.reset({ role: 'user' });
        this.showForm = false;
        this.loadData();
      },
      error: (err) => {
        this.errorMessage = err.error?.error || 'ADMIN_USERS.ERRORS.CREATE';
      },
    });
  }

  promoteToAdmin(user: AdminUser) {
    const companyId = this.companies[0]?.id;
    if (!companyId) {
      this.errorMessage = 'ADMIN_USERS.ERRORS.NO_COMPANY';
      return;
    }

    this.adminService.updateUserRole(user.id, { role: 'admin', companyId }).subscribe({
      next: () => {
        this.successMessage = 'ADMIN_USERS.SUCCESS_PROMOTE';
        this.loadData();
      },
      error: (err) => {
        this.errorMessage = err.error?.error || 'ADMIN_USERS.ERRORS.UPDATE';
      },
    });
  }

  revokeAdmin(user: AdminUser) {
    this.adminService.updateUserRole(user.id, { role: 'user' }).subscribe({
      next: () => {
        this.successMessage = 'ADMIN_USERS.SUCCESS_REVOKE';
        this.loadData();
      },
      error: (err) => {
        this.errorMessage = err.error?.error || 'ADMIN_USERS.ERRORS.UPDATE';
      },
    });
  }

  roleLabel(role: string): string {
    if (role === 'super_admin') return 'ADMIN_USERS.ROLE_SUPER';
    if (role === 'admin') return 'ADMIN_USERS.ROLE_ADMIN';
    return 'ADMIN_USERS.ROLE_USER';
  }
}
