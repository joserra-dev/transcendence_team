import { Component, HostListener, inject } from '@angular/core';
import { CommonModule, Location, NgIf } from '@angular/common';
import { NavigationEnd, Router, RouterLink } from '@angular/router';
import { filter, map, merge, of, startWith } from 'rxjs';
import { Auth } from '../../../core/services/auth';
import { LanguageService, Language } from '../../../core/services/language';
import { FormsModule } from '@angular/forms';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-header',
  imports: [CommonModule, NgIf, RouterLink, FormsModule, TranslateModule],
  templateUrl: './header.html',
  styleUrl: './header.scss',
})
export class Header {
  authService = inject(Auth);
  languageService = inject(LanguageService);
  private location = inject(Location);
  private router = inject(Router);
  menuOpen = false;
  mobileMenuOpen = false;

  showNavHistory$ = merge(
    of(this.router.url),
    this.router.events.pipe(
      filter((event): event is NavigationEnd => event instanceof NavigationEnd),
      map((event) => event.urlAfterRedirects)
    )
  ).pipe(
    startWith(this.router.url),
    map((url) => {
      const path = (url.split('?')[0].split('#')[0] || '/').replace(/\/+$/, '') || '/';
      return path !== '/';
    })
  );

  goBack(): void {
    this.location.back();
  }

  goForward(): void {
    this.location.forward();
  }

  logout() {
    this.authService.logout();
  }

  onLangChange(lang: Language) {
    this.languageService.changeLanguage(lang);
  }

  get isLogged(): boolean {
    return !!this.authService.getUser();
  }

  get isAdmin(): boolean {
    return this.authService.isAdmin();
  }

  get adminPanelLink(): string {
    return this.authService.isSuperAdmin() ? '/admin/companies' : '/admin/dashboard';
  }

  get logoLink(): string {
    const path = this.currentPath();
    if (!path.startsWith('/admin')) {
      return '/';
    }

    if (this.authService.isSuperAdmin()) {
      return '/admin/companies';
    }

    if (this.authService.isAdmin()) {
      return '/admin/dashboard';
    }

    return '/';
  }

  navigateLogo(event: Event): void {
    event.preventDefault();

    const target = this.logoLink.replace(/\/+$/, '') || '/';
    const path = this.currentPath();

    if (target === path) {
      this.router.navigate([target], {
        queryParams: { home: '1' },
        queryParamsHandling: 'merge',
      });
      return;
    }

    this.router.navigateByUrl(target);
  }

  private currentPath(): string {
    const path = this.router.url.split('?')[0].split('#')[0] || '/';
    return path.replace(/\/+$/, '') || '/';
  }

  toggleMenu(event: Event) {
    event.stopPropagation();
    this.menuOpen = !this.menuOpen;
  }

  closeMenu() {
  this.menuOpen = false;
  }

  @HostListener('document:click', ['$event'])
  onClickOutside(event: Event) {
    if (!this.menuOpen) return;

    const target = event.target as HTMLElement;

    const insideMenu =
      target.closest('.user-menu') ||
      target.closest('.user-icon-wrapper');

    if (!insideMenu) {
      this.menuOpen = false;
    }
  }

  toggleMobileMenu() {
    this.mobileMenuOpen = !this.mobileMenuOpen;
  }

  closeMobileMenu() {
    this.mobileMenuOpen = false;
  }
}
