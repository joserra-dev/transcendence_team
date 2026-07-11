import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, NavigationEnd, Router, RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { filter, map, merge, of, startWith } from 'rxjs';
import { toSignal } from '@angular/core/rxjs-interop';
import { Auth } from '../../../core/services/auth';

export interface BreadcrumbItem {
  labelKey: string;
  url?: string;
}

@Component({
  selector: 'app-breadcrumb',
  imports: [CommonModule, RouterLink, TranslateModule],
  templateUrl: './breadcrumb.html',
  styleUrl: './breadcrumb.scss',
})
export class Breadcrumb {
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  private auth = inject(Auth);

  items = toSignal(
    merge(
      of(null),
      this.router.events.pipe(filter((event) => event instanceof NavigationEnd))
    ).pipe(
      startWith(null),
      map(() => this.buildBreadcrumbs())
    ),
    { initialValue: [] as BreadcrumbItem[] }
  );

  onCrumbClick(event: MouseEvent, url: string): void {
    const path = this.currentPath();
    const target = url.replace(/\/+$/, '') || '/';

    if (path.startsWith('/admin') && target === '/') {
      event.preventDefault();
      void this.router.navigateByUrl(this.getHomeUrl(path));
    }
  }

  private buildBreadcrumbs(): BreadcrumbItem[] {
    const leaf = this.getLeafRoute();
    const override = leaf.snapshot.data['breadcrumbs'] as BreadcrumbItem[] | undefined;
    if (override?.length) {
      return this.normalizeItems(this.applySectionHome(override));
    }

    const collected: BreadcrumbItem[] = [];
    this.collectFromRoute(this.route.root, '', collected);

    if (collected.length === 0) {
      return [];
    }

    const path = this.currentPath();
    const homeUrl = this.getHomeUrl(path);
    const hasHomeCrumb = collected.some((item) => item.labelKey === 'BREADCRUMB.HOME');

    if (!hasHomeCrumb && (homeUrl !== '/' || path !== '/')) {
      collected.unshift({ labelKey: 'BREADCRUMB.HOME', url: homeUrl });
    }

    return this.normalizeItems(this.applySectionHome(collected));
  }

  private getLeafRoute(): ActivatedRoute {
    let route = this.route.root;
    while (route.firstChild) {
      route = route.firstChild;
    }
    return route;
  }

  private collectFromRoute(
    route: ActivatedRoute,
    url: string,
    items: BreadcrumbItem[]
  ): void {
    for (const child of route.children) {
      const segment = child.snapshot.url.map((part) => part.path).join('/');
      const nextUrl = segment ? `${url}/${segment}`.replace(/\/+/g, '/') : url;

      const labelKey = child.snapshot.data['breadcrumb'] as string | undefined;
      if (labelKey) {
        items.push({ labelKey, url: nextUrl || '/' });
      }

      this.collectFromRoute(child, nextUrl, items);
    }
  }

  private normalizeItems(items: BreadcrumbItem[]): BreadcrumbItem[] {
    const path = this.currentPath();

    return items.map((item, index) => {
      const isLast = index === items.length - 1;
      const url = item.url?.replace(/\/+$/, '') || '/';
      const isCurrent = url === path || (url === '/' && path === '/');

      if (isLast || isCurrent) {
        return { labelKey: item.labelKey };
      }

      return { labelKey: item.labelKey, url };
    });
  }

  private applySectionHome(items: BreadcrumbItem[]): BreadcrumbItem[] {
    const path = this.currentPath();
    const homeUrl = this.getHomeUrl(path);

    if (homeUrl === '/') {
      return items;
    }

    return items.map((item) =>
      item.labelKey === 'BREADCRUMB.HOME'
        ? { ...item, url: homeUrl }
        : item
    );
  }

  private currentPath(): string {
    const path = this.router.url.split('?')[0].split('#')[0] || '/';
    return path.replace(/\/+$/, '') || '/';
  }

  private getHomeUrl(path: string): string {
    if (this.isAdminSection(path)) {
      return this.auth.isSuperAdmin() ? '/admin/companies' : '/admin/dashboard';
    }

    return '/';
  }

  private isAdminSection(path: string): boolean {
    return path.startsWith('/admin');
  }
}
