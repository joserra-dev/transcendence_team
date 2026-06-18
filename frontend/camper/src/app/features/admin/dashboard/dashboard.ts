import { Component, inject, OnInit } from '@angular/core';
import { Admin } from '../../../core/services/admin';
import { Auth } from '../../../core/services/auth';
import { RouterLink } from '@angular/router';
import { Parking } from '../../../core/models/parking';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-dashboard',
  imports: [RouterLink, CommonModule, TranslateModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard implements OnInit {
  private adminService = inject(Admin);
  private authService = inject(Auth);

  parkings: Parking[] = [];
  isLoading = true;
  userName = '';
  isSuperAdmin = false;

  ngOnInit() {
    const user = this.authService.getUser();
    this.userName = user?.nombrePersona || user?.emailPersona || '';
    this.isSuperAdmin = this.authService.isSuperAdmin();
    this.loadParkings();
  }

  loadParkings() {
    this.adminService.getParkings().subscribe({
      next: (data) => {
        this.parkings = data;
        this.isLoading = false;
      },
      error: (err) => {
        console.error(err);
        this.isLoading = false;
      }
    });
  }

  logout() {
    this.authService.logoutAdmin();
  }
}
