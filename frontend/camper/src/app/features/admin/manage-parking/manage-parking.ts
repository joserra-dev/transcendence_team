import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { Admin } from '../../../core/services/admin';
import { Auth } from '../../../core/services/auth';
import { Parking, Space } from '../../../core/models/parking';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-manage-parking',
  imports: [CommonModule, ReactiveFormsModule, RouterLink, TranslateModule],
  templateUrl: './manage-parking.html',
  styleUrl: './manage-parking.scss',
})
export class ManageParking implements OnInit {
  private fb = inject(FormBuilder);
  private adminService = inject(Admin);
  private authService = inject(Auth);
  private route = inject(ActivatedRoute);
  private router = inject(Router);

  parkingId: number | null = null;
  companyId: number | null = null;
  isEditMode = false;
  isLoading = false;

  successMessage = '';
  errorMessage = '';
  spotErrorMessage = '';

  parkingForm: FormGroup = this.fb.group({
    nombreParking: ['', Validators.required],
    provinciaParking: [''],
    municipioParking: ['', Validators.required],
    webParking: [''],
    telefonoParking: [''],
    emailParking: ['', [Validators.required, Validators.email]],
    personaContactoParking: [''],
    isActivoParking: [true],
    tieneElectricidadParking: [false],
    tieneResidualesParking: [false],
    tienePlazasVipParking: [false]
  });

  plazas: Space[] = [];
  showSpotModal = false;
  currentSpotId: number | null = null;

  spotForm: FormGroup = this.fb.group({
    nombre: ['', Validators.required],
    precio: [0, [Validators.required, Validators.min(0)]],
    estado: ['0'],
    esVip: [false],
    tieneElectricidad: [false]
  });

  ngOnInit() {
    const companyIdParam = this.route.snapshot.queryParamMap.get('companyId');
    this.companyId = companyIdParam ? Number(companyIdParam) : null;

    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.parkingId = Number(id);
      this.isEditMode = true;
      this.loadParking(this.parkingId);
    }
  }

  get backLink(): string[] {
    if (this.authService.isSuperAdmin() && this.companyId) {
      return ['/admin/companies', String(this.companyId), 'parkings'];
    }
    return ['/admin/dashboard'];
  }

  // --- GESTIÓN DE INFORMACIÓN GENERAL DEL PARKING ---

  loadParking(id: number) {
    this.isLoading = true;
    this.adminService.getParkingById(id).subscribe({
      next: (data) => {
        this.parkingForm.patchValue({
          nombreParking: data.name,
          municipioParking: data.localidad || data.municipality,
          provinciaParking: data.province,

          webParking: data.web,
          telefonoParking: data.telephone,
          emailParking: data.email,
          personaContactoParking: data.contact_person,

          tieneElectricidadParking: data.tomaElectricidad || data.has_electricity,

          tieneResidualesParking: data.limpiezaAguasResiduales || data.has_waste_disposal,

          tienePlazasVipParking: data.plazasVip || data.has_vip_spots,

          isActivoParking: data.isActive !== undefined ? data.isActive : true
        });

        this.plazas = data.plazasResponse || data.spaces || [];
        if (!this.companyId && data.id_company) {
          this.companyId = data.id_company;
        }
        this.isLoading = false;
      },
      error: (err) => {
        console.error(err);
        this.isLoading = false;
      }
    });
  }

  saveParking() {
    this.clearMessages();

    if (this.parkingForm.invalid) {
      this.parkingForm.markAllAsTouched();
      return;
    }

    this.isLoading = true;
    const formData = this.parkingForm.value;

    if (this.isEditMode && this.parkingId) {
      const updateData = { ...formData, idParking: this.parkingId };
      this.adminService.updateParking(updateData).subscribe({
        next: () => {
          this.showSuccess('Parking actualizado correctamente');
          this.isLoading = false;
        },
        error: (err) => {
            if (err.status === 200) {
             this.showSuccess('Parking actualizado correctamente');
             this.isLoading = false;
          } else {
             console.error(err);
             this.errorMessage = 'Error al actualizar el parking. Inténtalo de nuevo.';
             this.isLoading = false;
          }
        }
      });
    } else {
      const createData = this.companyId
        ? { ...formData, companyId: this.companyId }
        : formData;
      this.adminService.createParking(createData).subscribe({
        next: () => {
          this.showSuccess('Parking creado correctamente');
          this.router.navigate(this.backLink);
        },
        error: (err) => {
          console.error(err);
          this.errorMessage ='Error al crear el parking';
          this.isLoading = false;
        }
      });
    }
  }

  // --- GESTIÓN DE PLAZAS ---

  openSpotModal(spot?: Space) {
    this.spotErrorMessage = '';
    this.showSpotModal = true;
    if (spot) {
      this.currentSpotId = spot.id;
      this.spotForm.patchValue(spot);
    } else {
      this.currentSpotId = null;
      this.spotForm.reset({ estado: '0', precio: 0, esVip: false, tieneElectricidad: false });
    }
  }

  closeSpotModal() {
    this.showSpotModal = false;
    this.currentSpotId = null;
    this.spotErrorMessage = '';
  }

  saveSpot() {
    if (this.spotForm.invalid || !this.parkingId) return;

    const spotData = this.spotForm.value;

    if (this.currentSpotId) {
      this.adminService.updateSpot(this.parkingId, this.currentSpotId, spotData).subscribe({
        next: (updatedSpot) => {
          const index = this.plazas.findIndex(p => p.id === this.currentSpotId);
          if (index !== -1) {
             this.plazas[index] = { ...this.plazas[index], ...updatedSpot };
          }
          this.closeSpotModal();
          this.showSuccess('Plaza actualizada correctamente');
        },
        error: () => this.spotErrorMessage = 'MANAGE_PARKING.ERRORS.UPDATE_SPOT'
      });
    } else {
      this.adminService.createSpot(this.parkingId, spotData).subscribe({
        next: (newSpot) => {
          this.plazas.push(newSpot);
          this.closeSpotModal();
          this.showSuccess('Plaza creada correctamente');
        },
        error: () => this.spotErrorMessage = 'MANAGE_PARKING.ERRORS.CREATE_SPOT'
      });
    }
  }

  private clearMessages() {
    this.successMessage = '';
    this.errorMessage = '';
    this.spotErrorMessage = '';
  }

  private showSuccess(msg: string) {
    this.successMessage = msg;
    setTimeout(() => {
        this.successMessage = '';
    }, 3000);
  }
}
