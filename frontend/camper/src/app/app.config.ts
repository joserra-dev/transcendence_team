import { ApplicationConfig, provideBrowserGlobalErrorListeners, provideZoneChangeDetection, importProvidersFrom, APP_INITIALIZER } from '@angular/core';
import { provideRouter,withDebugTracing } from '@angular/router';
import { HttpClient, provideHttpClient, withInterceptors } from '@angular/common/http';
import { routes } from './app.routes';
import { languageInterceptor } from './core/interceptors/language';
import { authInterceptor } from './core/interceptors/auth-interceptor';
import { Observable, catchError, of } from 'rxjs';

import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { LanguageService } from './core/services/language';

export class CustomTranslateLoader implements TranslateLoader {
  constructor(private http: HttpClient) {}

  getTranslation(lang: string): Observable<any> {
    const timestamp = new Date().getTime();
    return this.http.get(`/assets/i18n/${lang}.json?v=${timestamp}`).pipe(
       catchError(() => of({})) 
    );
  }
}

export function HttpLoaderFactory(http: HttpClient) {
  return new CustomTranslateLoader(http);
}

export function appInitializerFactory(language: LanguageService) {
  return () => language.init();
}

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes), 
    provideHttpClient(
      withInterceptors([languageInterceptor, authInterceptor])
    ),
  
    importProvidersFrom(
      TranslateModule.forRoot({
        loader: {
          provide: TranslateLoader,
          useFactory: HttpLoaderFactory,
          deps: [HttpClient]
        },
      })
    ),

    {
      provide: APP_INITIALIZER,
      useFactory: appInitializerFactory,
      deps: [LanguageService],
      multi: true
    }
  ]
};