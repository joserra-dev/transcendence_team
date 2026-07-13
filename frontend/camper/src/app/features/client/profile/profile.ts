import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators, AbstractControl, ValidationErrors } from '@angular/forms';
import { UserService } from '../../../core/services/user';
import { User } from '../../../core/models/user';

interface UserFriend {
  id: number;
  email: string;
  nombrePersona: string;
  apellidosPersona: string;
  avatar: string;
  role: string;
}
import { CustomValidators } from '../../../shared/validators/custom-validators/custom-validators';
import { TranslateModule } from '@ngx-translate/core';
import { FormsModule } from '@angular/forms';
import { FriendService } from '../../../core/services/friend';

@Component({
  selector: 'app-profile',
  imports: [CommonModule, ReactiveFormsModule, TranslateModule, FormsModule],
  templateUrl: './profile.html',
  styleUrl: './profile.scss',
})
export class Profile implements OnInit {
  private fb = inject(FormBuilder);
  private userService = inject(UserService);
  private friendService = inject(FriendService);

  currentUser: User | null = null;
  friends: UserFriend[] = [];
  newFriendEmail = '';
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
    avatarPersona: [{ value: '', disabled: true }],
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

  get isDniEditable(): boolean {
    return !this.currentUser?.dniPersona?.trim();
  }

  ngOnInit() {
    this.loadUserProfile();
    this.loadFriends();
  }

  loadUserProfile() {
    this.isLoading = true;
    this.userService.getMe().subscribe({
      next: (user: User) => {
        this.currentUser = user;
        this.profileForm.patchValue({
          ...user,
          avatarPersona: user.avatar || '',
        });
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error cargando perfil:', err);
        this.errorMessage = 'PROFILE.ERROR.DATA';
        this.isLoading = false;
      }
    });
  }

  loadFriends() {
    this.friendService.listFriends().subscribe({
      next: (data) => {
        this.friends = data || [];
      },
      error: (err) => {
        console.error('Error cargando amigos:', err);
      }
    });
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

  enableEdit() {
    this.isEditing = true;
    this.successMessage = '';
    this.errorMessage = '';
    // Habilitamos todos los campos editables
    [
      'nombrePersona', 'apellidosPersona', 'fecNacimientoPersona',
      'metodoPago', 'avatarPersona', 'ibanPersona', 'tarjeta', 'passPersona', 'confirmPassPersona'
    ].forEach(field => this.profileForm.get(field)?.enable());

    if (this.isDniEditable) {
      const dniControl = this.profileForm.get('dniPersona');
      dniControl?.setValidators([CustomValidators.documentoIdentidad]);
      dniControl?.enable();
      dniControl?.updateValueAndValidity();
    }
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
        avatarPersona: this.currentUser.avatar,
        ibanPersona: this.currentUser.ibanPersona,
        tarjeta: this.currentUser.tarjeta,
        passPersona: '',
        confirmPassPersona: ''
      });
    }

    // Deshabilitamos todos los campos editables al cancelar
    [
      'nombrePersona', 'apellidosPersona', 'fecNacimientoPersona',
      'metodoPago', 'avatarPersona', 'ibanPersona', 'tarjeta', 'passPersona', 'confirmPassPersona'
    ].forEach(field => this.profileForm.get(field)?.disable());

    const dniControl = this.profileForm.get('dniPersona');
    dniControl?.clearValidators();
    dniControl?.disable();
    dniControl?.updateValueAndValidity();
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
      next: () => {
        this.successMessage = 'PROFILE.SUCCESS.UPDATED';
        const updatedUser = {
          ...this.currentUser!,
          ...formData,
          avatar: formData.avatarPersona,
          dniPersona: formData.dniPersona || this.currentUser?.dniPersona,
        };
        this.currentUser = updatedUser;
        sessionStorage.setItem('user', JSON.stringify(updatedUser));
        this.isEditing = false;
        this.isLoading = false;
        this.profileForm.patchValue({ passPersona: '', confirmPassPersona: '' });
        this.profileForm.get('dniPersona')?.clearValidators();
        this.profileForm.get('dniPersona')?.disable();
      },
      error: (err) => {
        console.error(err);
        const backendError = err?.error;
        if (typeof backendError === 'object' && backendError?.error) {
          this.errorMessage = backendError.error;
        } else if (typeof backendError === 'string') {
          this.errorMessage = backendError;
        } else {
          this.errorMessage = 'PROFILE.ERROR.CHANGES';
        }
        this.isLoading = false;
      }
    });
  }

  isInvalid(field: string): boolean {
    const control = this.profileForm.get(field);
    return !!(control && control.invalid && (control.dirty || control.touched));
  }

  addFriend() {
    if (!this.newFriendEmail || this.newFriendEmail.trim() === '') {
      this.errorMessage = 'FRIENDS.ERROR.EMAIL_REQUIRED';
      return;
    }
    this.friendService.addFriend(Number(this.newFriendEmail)).subscribe({
      next: () => {
        this.successMessage = 'FRIENDS.SUCCESS.ADDED';
        this.newFriendEmail = '';
        this.errorMessage = '';
        this.loadFriends();
      },
      error: (err) => {
        console.error('Error agregando amigo:', err);
        this.errorMessage = 'FRIENDS.ERROR.NOT_FOUND';
      }
    });
  }

  removeFriend(friendId: number) {
    this.friendService.removeFriend(friendId).subscribe({
      next: () => {
        this.friends = this.friends.filter(f => f.id !== friendId);
        this.successMessage = 'FRIENDS.SUCCESS.REMOVED';
        this.errorMessage = '';
      },
      error: (err) => {
        console.error('Error eliminando amigo:', err);
        this.errorMessage = 'FRIENDS.ERROR.REMOVE';
      }
    });
  }
}
