import { Component, inject, signal } from '@angular/core';
import { RouterOutlet, RouterModule } from '@angular/router';
import { Header } from "./shared/components/header/header";
import { Footer } from "./shared/components/footer/footer";
import { LanguageService } from './core/services/language';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterModule, Header, Footer],
  standalone: true,
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('camper');
  languageService = inject(LanguageService);
}
