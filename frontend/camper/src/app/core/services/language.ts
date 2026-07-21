import { Injectable, signal, inject } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';

export type Language = 'es' | 'en' | 'eu';

@Injectable({
  providedIn: 'root'
})
export class LanguageService {
  private translate = inject(TranslateService);
  private readonly SUPPORTED_LANGS: Language[] = ['es', 'en', 'eu'];
  private readonly DEFAULT_LANG: Language = 'es';

  // Signal con el idioma inicial validado desde localStorage
  currentLang = signal<Language>(this.getInitialLanguage());

  constructor() {
    // Configuración base de ngx-translate
    this.translate.addLangs(this.SUPPORTED_LANGS);
    this.translate.setDefaultLang(this.DEFAULT_LANG);

    // Aplicamos el idioma detectado al iniciar la app
    this.applyLanguage(this.currentLang());
  }

  changeLanguage(lang: Language) {
    if (!this.SUPPORTED_LANGS.includes(lang)) return;

    this.currentLang.set(lang);
    localStorage.setItem('lang', lang);
    this.applyLanguage(lang);
  }

  private applyLanguage(lang: Language) {
    this.translate.use(lang);
  }

  private getInitialLanguage(): Language {
    const savedLang = localStorage.getItem('lang') as Language;
    
    // Verificamos que exista y que sea un idioma válido
    if (savedLang && this.SUPPORTED_LANGS.includes(savedLang)) {
      return savedLang;
    }

    return this.DEFAULT_LANG;
  }
}