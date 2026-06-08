import { Component, HostListener, inject } from '@angular/core';
import { CommonModule, NgIf } from '@angular/common';
import { RouterLink } from '@angular/router';
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
  menuOpen = false;
  mobileMenuOpen = false;

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
