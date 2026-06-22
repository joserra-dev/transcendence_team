import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-legal-page',
  standalone: true,
  imports: [TranslateModule],
  templateUrl: './legal-page.html',
  styleUrl: './legal-page.scss',
})
export class LegalPage implements OnInit, OnDestroy {
  private route = inject(ActivatedRoute);
  private paramsSubscription!: Subscription;
  pageType: 'privacy' | 'terms' = 'privacy';

  ngOnInit() {
    this.paramsSubscription = this.route.paramMap.subscribe(params => {
      const type = params.get('type');
      this.pageType = type === 'terms' ? 'terms' : 'privacy';
      window.scrollTo({ top: 0, behavior: 'auto' });
    });
  }

  ngOnDestroy() {
    this.paramsSubscription?.unsubscribe();
  }

  get titleKey(): string {
    return this.pageType === 'privacy' ? 'LEGAL.PRIVACY_TITLE' : 'LEGAL.TERMS_TITLE';
  }

  get bodyKey(): string {
    return this.pageType === 'privacy' ? 'LEGAL.PRIVACY_BODY' : 'LEGAL.TERMS_BODY';
  }
}
