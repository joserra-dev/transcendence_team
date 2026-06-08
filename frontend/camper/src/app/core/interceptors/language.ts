import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { LanguageService } from '../services/language';

export const languageInterceptor: HttpInterceptorFn = (req, next) => {
  const langService = inject(LanguageService);
  const currentLang = langService.currentLang();

  const reqWithHeader = req.clone({
    setHeaders: {
      'Accept-Language': currentLang
    }
  });

  return next(reqWithHeader);
};