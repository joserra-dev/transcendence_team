import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { UserService } from '../../../core/services/user';
import { User } from '../../../core/models/user';
import { CustomValidators } from '../../../shared/validators/custom-validators/custom-validators';
import { TranslateModule } from '@ngx-translate/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-profile',
  imports: [CommonModule, ReactiveFormsModule, TranslateModule, FormsModule],
  templateUrl: './profile.html',
  styleUrl: './profile.scss',
})
export class Profile implements OnInit {
  private fb = inject(FormBuilder);
  private userService = inject(UserService);
  
  currentUser: User | null = null;
  isLoading = true;
  isEditing = false;
  successMessage = '';
  errorMessage = '';

  profileForm: FormGroup = this.fb.group({
    dniPersona: [{ value: '', disabled: true }],
    emailPersona: [{ value: '', disabled: true }],
    nombrePersona: [{ value: '', disabled: true }, Validators.required],
    apellidosPersona: [{ value: '', disabled: true }, Validators.required],
    fecNacimientoPersona: [{ value: '', disabled: true }, [Validators.required, CustomValidators.mayorDeEdad]],
    tarjeta: [{ value: '', disabled: true }],
    passPersona: [{ value: '', disabled: true }],
    confirmPassPersona: [{ value: '', disabled: true }]
  }, {
    validators: [
      CustomValidators.matchPasswords('passPersona', 'confirmPassPersona'),
    ]
  });

  ngOnInit() {
    this.loadUserProfile();
  }

  loadUserProfile() {
    this.isLoading = true;
    this.userService.getMe().subscribe({
      next: (user: User) => {
        this.currentUser = user;
        this.profileForm.patchValue(user);
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = 'PROFILE.ERROR.DATA';
        this.isLoading = false;
      }
    });
  }

  
  enableEdit() {
    this.isEditing = true;
    this.successMessage = '';
    this.errorMessage = '';
    // Habilitamos todos los campos editables
    [
      'nombrePersona', 'apellidosPersona','dniPersona' ,'fecNacimientoPersona',
      'passPersona', 'confirmPassPersona'
    ].forEach(field => this.profileForm.get(field)?.enable());
  }

  cancelEdit() {
    this.isEditing = false;
    this.errorMessage = '';
    this.successMessage = '';

    if (this.currentUser) {
      this.profileForm.reset({
        dniPersona: this.currentUser.dniPersona,
        emailPersona: this.currentUser.emailPersona,
        nombrePersona: this.currentUser.nombrePersona,
        apellidosPersona: this.currentUser.apellidosPersona,
        fecNacimientoPersona: this.currentUser.fecNacimientoPersona,
        passPersona: '',
        confirmPassPersona: ''
      });
    }

    // Deshabilitamos todos los campos editables al cancelar
    [
      'nombrePersona', 'apellidosPersona', 'dniPersona' ,'fecNacimientoPersona',
      'passPersona', 'confirmPassPersona'
    ].forEach(field => this.profileForm.get(field)?.disable());
  }

  saveChanges() {
    if (this.profileForm.invalid) {
      this.profileForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    const formData = this.profileForm.getRawValue();
    const updateData = {
      ...formData,
      admin: this.currentUser?.admin || false
    };

    this.userService.updateProfile(updateData).subscribe({
      next: (response) => {
        this.successMessage = response.mensaje;
        const updatedUser = {
          ...this.currentUser!,
          ...formData
        };
        this.currentUser = updatedUser;
        sessionStorage.setItem('user', JSON.stringify(updatedUser));
        this.isEditing = false;
        this.isLoading = false;
        this.profileForm.patchValue({ passPersona: '', confirmPassPersona: '' });
      },
      error: (err) => {
        this.errorMessage = 'PROFILE.ERROR.CHANGES';
        this.isLoading = false;
      }
    });
  }

  isInvalid(field: string): boolean {
    const control = this.profileForm.get(field);
    return !!(control && control.invalid && (control.dirty || control.touched));
  }
}
