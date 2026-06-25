import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { Admin } from '../../../core/services/admin';
import { Parking } from '../../../core/models/parking';
import { Company } from '../../../core/models/user';

@Component({
  selector: 'app-company-parkings',
  imports: [CommonModule, RouterLink, TranslateModule],
  templateUrl: './company-parkings.html',
  styleUrl: './company-parkings.scss',
})
export class CompanyParkings implements OnInit {
  private adminService = inject(Admin);
  private route = inject(ActivatedRoute);

  companyId!: number;
  company: Company | null = null;
  parkings: Parking[] = [];
  isLoading = true;

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    this.companyId = Number(id);
    this.loadData();
  }

  loadData() {
    this.isLoading = true;

    this.adminService.getCompanies().subscribe({
      next: (companies) => {
        this.company = companies.find((c) => c.id === this.companyId) || null;
      },
    });

    this.adminService.getParkings(this.companyId).subscribe({
      next: (parkings) => {
        this.parkings = parkings;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      },
    });
  }
}
