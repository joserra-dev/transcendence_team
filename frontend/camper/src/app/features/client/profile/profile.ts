import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { UserService } from '../../../core/services/user';
import { User } from '../../../core/models/user';
import { CustomValidators } from '../../../shared/validators/custom-validators/custom-validators';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-profile',
  imports: [CommonModule, ReactiveFormsModule, TranslateModule],
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
    nombrePersona: ['', Validators.required],
    apellidosPersona: ['', Validators.required],
    fecNacimientoPersona: ['', [Validators.required, CustomValidators.mayorDeEdad]],
    ibanPersona: ['', [Validators.required, CustomValidators.ibanValido]],
    passPersona: [''],
    confirmPassPersona: ['']
  }, {
    validators: CustomValidators.matchPasswords('passPersona', 'confirmPassPersona')
  });

  ngOnInit() {
    this.loadUserProfile();
  }

  loadUserProfile() {
    this.isLoading = true;
    this.userService.getMe().subscribe({
      next: (user: User) => {
        this.profileForm.patchValue(user);
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error cargando perfil:', err);
        this.errorMessage = 'PROFILE.ERROR.DATA';
        this.isLoading = false;
      }
    });
  }

  enableEdit() {
    this.isEditing = true;
    this.successMessage = '';
    this.errorMessage = '';
  }

  cancelEdit() {
    this.isEditing = false;
    this.errorMessage = '';
    this.successMessage = '';


    this.profileForm.get('passPersona')?.reset();
    this.profileForm.get('confirmPassPersona')?.reset();

    if (this.currentUser) {
      this.profileForm.reset({
        dniPersona: this.currentUser.dniPersona,
        emailPersona: this.currentUser.emailPersona,
        nombrePersona: this.currentUser.nombrePersona,
        apellidosPersona: this.currentUser.apellidosPersona,
        fecNacimientoPersona: this.currentUser.fecNacimientoPersona,
        ibanPersona: this.currentUser.ibanPersona
      });
    }
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
      next: (responseMessage: string) => {
        this.successMessage = responseMessage;
        this.currentUser = { ...this.currentUser!, ...formData };
        this.isEditing = false;
        this.isLoading = false;
        this.profileForm.patchValue({ passPersona: '', confirmPassPersona: '' });
      },
      error: (err) => {
        console.error(err);
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
