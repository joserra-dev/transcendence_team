import { HttpInterceptorFn } from '@angular/common/http';

export const languageInterceptor: HttpInterceptorFn = (req, next) => {

  if (req.url.includes('/assets/i18n/')) {
    return next(req);
  }

  const lang = localStorage.getItem('lang') || 'es';

  const reqWithHeader = req.clone({
    setHeaders: {
      'Accept-Language': lang
    }
  });

  return next(reqWithHeader);
};
