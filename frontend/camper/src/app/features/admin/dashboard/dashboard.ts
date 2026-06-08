import { Component, inject, OnInit } from '@angular/core';
import { Admin } from '../../../core/services/admin';
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
  parkings: Parking[] = [];
  isLoading = true;

  ngOnInit() {
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
}
