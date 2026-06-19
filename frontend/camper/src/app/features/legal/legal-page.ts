import { Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-legal-page',
  standalone: true,
  imports: [TranslateModule],
  templateUrl: './legal-page.html',
  styleUrl: './legal-page.scss',
})
export class LegalPage implements OnInit {
  private route = inject(ActivatedRoute);
  pageType: 'privacy' | 'terms' = 'privacy';

  ngOnInit() {
    const type = this.route.snapshot.paramMap.get('type');
    this.pageType = type === 'terms' ? 'terms' : 'privacy';
  }

  get titleKey(): string {
    return this.pageType === 'privacy' ? 'LEGAL.PRIVACY_TITLE' : 'LEGAL.TERMS_TITLE';
  }

  get bodyKey(): string {
    return this.pageType === 'privacy' ? 'LEGAL.PRIVACY_BODY' : 'LEGAL.TERMS_BODY';
  }
}
