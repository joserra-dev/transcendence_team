import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators, FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { Admin } from '../../../core/services/admin';
import { AdminUser, Company } from '../../../core/models/user';
import { ConfirmDialog } from '../../../shared/components/confirm-dialog/confirm-dialog';

@Component({
  selector: 'app-manage-users',
  imports: [CommonModule, ReactiveFormsModule, FormsModule, RouterLink, TranslateModule, ConfirmDialog],
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
  editingUserId: number | null = null;
  promotingUserId: number | null = null;
  promoteCompanyId: number | null = null;
  successMessage = '';
  errorMessage = '';
  showRevokeConfirm = false;
  revokeConfirmParams: Record<string, string> = {};
  private userPendingRevoke: AdminUser | null = null;
  showDeleteConfirm = false;
  deleteConfirmParams: Record<string, string> = {};
  private userPendingDelete: AdminUser | null = null;

  filterRole = 'all';
  filterCompanyId: number | 'all' = 'all';
  sortOrder: 'asc' | 'desc' = 'asc';

  userForm: FormGroup = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]],
    nombre: ['', Validators.required],
    apellidos: [''],
    dni: [''],
    role: ['user', Validators.required],
    companyId: [null],
  });

  editForm: FormGroup = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: [''],
    nombre: ['', Validators.required],
    apellidos: [''],
    dni: [''],
    role: ['user', Validators.required],
    companyId: [null],
  });

  ngOnInit() {
    this.loadData();
    this.setupRoleValidators(this.userForm);
    this.setupRoleValidators(this.editForm);
  }

  private setupRoleValidators(form: FormGroup) {
    form.get('role')?.valueChanges.subscribe((role) => {
      const companyControl = form.get('companyId');
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
    this.cancelEditUser();
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

  startEditUser(user: AdminUser) {
    this.editingUserId = user.id;
    this.promotingUserId = null;
    this.editForm.patchValue({
      email: user.email,
      password: '',
      nombre: user.nombre,
      apellidos: user.apellidos,
      dni: user.dni,
      role: user.role,
      companyId: user.companyId,
    });
  }

  cancelEditUser() {
    this.editingUserId = null;
    this.editForm.reset({ role: 'user' });
  }

  saveUser() {
    if (!this.editingUserId || this.editForm.invalid) {
      this.editForm.markAllAsTouched();
      return;
    }

    const data = { ...this.editForm.value };
    if (!data.password) {
      delete data.password;
    }

    this.adminService.updateUser(this.editingUserId, data).subscribe({
      next: () => {
        this.successMessage = 'ADMIN_USERS.SUCCESS_UPDATE';
        this.cancelEditUser();
        this.loadData();
      },
      error: (err) => {
        this.errorMessage = err.error?.error || 'ADMIN_USERS.ERRORS.UPDATE';
      },
    });
  }

  startPromote(user: AdminUser) {
    this.promotingUserId = user.id;
    this.promoteCompanyId = user.companyId ?? this.companies[0]?.id ?? null;
    this.cancelEditUser();
  }

  cancelPromote() {
    this.promotingUserId = null;
    this.promoteCompanyId = null;
  }

  confirmPromote() {
    if (!this.promotingUserId || !this.promoteCompanyId) {
      this.errorMessage = 'ADMIN_USERS.ERRORS.NO_COMPANY';
      return;
    }

    this.adminService.updateUserRole(this.promotingUserId, {
      role: 'admin',
      companyId: this.promoteCompanyId,
    }).subscribe({
      next: () => {
        this.successMessage = 'ADMIN_USERS.SUCCESS_PROMOTE';
        this.cancelPromote();
        this.loadData();
      },
      error: (err) => {
        this.errorMessage = err.error?.error || 'ADMIN_USERS.ERRORS.UPDATE';
      },
    });
  }

  revokeAdmin(user: AdminUser) {
    this.userPendingRevoke = user;
    this.revokeConfirmParams = { name: this.fullName(user) || user.email };
    this.showRevokeConfirm = true;
  }

  cancelRevokeAdmin() {
    this.showRevokeConfirm = false;
    this.userPendingRevoke = null;
  }

  confirmRevokeAdmin() {
    const user = this.userPendingRevoke;
    if (!user) {
      return;
    }

    this.showRevokeConfirm = false;
    this.userPendingRevoke = null;

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

  deleteUser(user: AdminUser) {
    this.userPendingDelete = user;
    this.deleteConfirmParams = { name: this.fullName(user) || user.email };
    this.showDeleteConfirm = true;
  }

  cancelDeleteUser() {
    this.showDeleteConfirm = false;
    this.userPendingDelete = null;
  }

  confirmDeleteUser() {
    const user = this.userPendingDelete;
    if (!user) {
      return;
    }

    this.showDeleteConfirm = false;
    this.userPendingDelete = null;

    this.adminService.deleteUser(user.id).subscribe({
      next: () => {
        this.successMessage = 'ADMIN_USERS.SUCCESS_DELETE';
        this.cancelEditUser();
        this.cancelPromote();
        this.loadData();
      },
      error: (err) => {
        this.errorMessage = err.error?.error || 'ADMIN_USERS.ERRORS.DELETE';
      },
    });
  }

  roleLabel(role: string): string {
    if (role === 'super_admin') return 'ADMIN_USERS.ROLE_SUPER';
    if (role === 'admin') return 'ADMIN_USERS.ROLE_ADMIN';
    return 'ADMIN_USERS.ROLE_USER';
  }

  fullName(user: AdminUser): string {
    return `${user.nombre || ''} ${user.apellidos || ''}`.trim();
  }

  get filteredUsers(): AdminUser[] {
    let result = [...this.users];

    if (this.filterRole !== 'all') {
      result = result.filter((user) => user.role === this.filterRole);
    }

    if (this.filterCompanyId !== 'all') {
      result = result.filter((user) => user.companyId === this.filterCompanyId);
    }

    result.sort((a, b) => {
      const cmp = this.fullName(a).localeCompare(this.fullName(b), 'es', { sensitivity: 'base' });
      return this.sortOrder === 'asc' ? cmp : -cmp;
    });

    return result;
  }

  toggleSortOrder(): void {
    this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
  }
}
