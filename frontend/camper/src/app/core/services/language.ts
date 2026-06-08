import { Injectable, signal, inject } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';

export type Language = 'es' | 'en' | 'eu';

@Injectable({
  providedIn: 'root'
})
export class LanguageService {
  private translate = inject(TranslateService);

  currentLang = signal<Language>(
    (localStorage.getItem('lang') as Language) || 'es'
  );

  constructor() {
    const initialLang = this.currentLang();
    this.translate.use(initialLang);
  }

  changeLanguage(lang: Language) {
    this.currentLang.set(lang);
    localStorage.setItem('lang', lang)
    this.translate.use(lang);
    console.log('Language changed to:', lang);
  }
}
