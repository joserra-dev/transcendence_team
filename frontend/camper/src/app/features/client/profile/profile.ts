import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
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
    nombrePersona: [{ value: '', disabled: true }, Validators.required],
    apellidosPersona: [{ value: '', disabled: true }, Validators.required],
    fecNacimientoPersona: [{ value: '', disabled: true }, [Validators.required, CustomValidators.mayorDeEdad]],
    metodoPago: [{ value: 'iban', disabled: true }, Validators.required],
    ibanPersona: [{ value: '', disabled: true }],
    tarjeta: [{ value: '', disabled: true }],
    passPersona: [{ value: '', disabled: true }],
    confirmPassPersona: [{ value: '', disabled: true }]
  }, {
    validators: [
      CustomValidators.matchPasswords('passPersona', 'confirmPassPersona'),
      this.paymentMethodValidator()
    ]
  });

  ngOnInit() {
    this.loadUserProfile();
  }

  paymentMethodValidator() {
    return (form: AbstractControl): ValidationErrors | null => {
      const metodo = form.get('metodoPago')?.value;
      const iban = form.get('ibanPersona')?.value;
      const tarjeta = form.get('tarjeta')?.value;

      if (metodo === 'iban') {
        if (!iban || iban.trim() === '') {
          form.get('ibanPersona')?.setErrors({ required: true });
          return { paymentRequired: true };
        }
        const regex = /^ES\d{22}$/i;
        if (!regex.test(iban)) {
          form.get('ibanPersona')?.setErrors({ ibanInvalido: true });
          return { ibanInvalido: true };
        }
        form.get('ibanPersona')?.setErrors(null);
      } else if (metodo === 'tarjeta') {
        if (!tarjeta || tarjeta.trim() === '') {
          form.get('tarjeta')?.setErrors({ required: true });
          return { paymentRequired: true };
        }
        const regex = /^\d{16}$/;
        if (!regex.test(tarjeta)) {
          form.get('tarjeta')?.setErrors({ tarjetaInvalida: true });
          return { tarjetaInvalida: true };
        }
        form.get('tarjeta')?.setErrors(null);
      } else {
        form.get('ibanPersona')?.setErrors(null);
        form.get('tarjeta')?.setErrors(null);
      }
      return null;
    };
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
    // Habilitamos todos los campos editables
    ['nombrePersona', 'apellidosPersona', 'fecNacimientoPersona',
     'metodoPago', 'ibanPersona', 'tarjeta', 'passPersona', 'confirmPassPersona'
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
        metodoPago: this.currentUser.metodoPago || 'iban',
        ibanPersona: this.currentUser.ibanPersona,
        tarjeta: this.currentUser.tarjeta,
        passPersona: '',
        confirmPassPersona: ''
      });
    }

    // Deshabilitamos todos los campos editables al cancelar
    ['nombrePersona', 'apellidosPersona', 'fecNacimientoPersona',
     'metodoPago', 'ibanPersona', 'tarjeta', 'passPersona', 'confirmPassPersona'
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
      next: (responseMessage: string) => {
        this.successMessage = responseMessage;
        const updatedUser = { ...this.currentUser!, ...formData };
        this.currentUser = updatedUser;
        sessionStorage.setItem('user', JSON.stringify(updatedUser));
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
