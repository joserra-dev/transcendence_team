import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
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
  successMessage = '';
  errorMessage = '';

  profileForm: FormGroup = this.fb.group({
    dniPersona: [''],
    emailPersona: [{ value: '', disabled: true }],
    nombrePersona: ['', Validators.required],
    apellidosPersona: ['', Validators.required],
    fecNacimientoPersona: ['', [Validators.required, CustomValidators.mayorDeEdad]],
    tarjeta: [{ value: '', disabled: true }],
    passPersona: [''],
    confirmPassPersona: ['']
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
      error: () => {
        this.successMessage = '';
        this.errorMessage = 'PROFILE.ERROR.DATA';
        this.isLoading = false;
      }
    });
  }

  saveChanges() {
    if (this.profileForm.invalid) {
      this.profileForm.markAllAsTouched();
      this.successMessage = '';
      this.errorMessage = 'PROFILE.ERROR.VALIDATION';
      return;
    }

    this.isLoading = true;
    this.successMessage = '';
    this.errorMessage = '';
    const formData = this.profileForm.getRawValue();
    const updateData = {
      ...formData,
      admin: this.currentUser?.admin || false
    };

    this.userService.updateProfile(updateData).subscribe({
      next: (response) => {
        this.errorMessage = '';
        this.successMessage = response.mensaje;
        const updatedUser = {
          ...this.currentUser!,
          ...formData
        };
        this.currentUser = updatedUser;
        sessionStorage.setItem('user', JSON.stringify(updatedUser));
        this.isLoading = false;
        this.profileForm.patchValue({ passPersona: '', confirmPassPersona: '' });
      },
      error: () => {
        this.successMessage = '';
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
