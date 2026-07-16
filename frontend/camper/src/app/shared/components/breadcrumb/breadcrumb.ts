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

  private buildBreadcrumbs(): BreadcrumbItem[] {
    const leaf = this.getLeafRoute();
    const override = leaf.snapshot.data['breadcrumbs'] as BreadcrumbItem[] | undefined;
    if (override?.length) {
      return this.normalizeItems(override);
    }

    const collected: BreadcrumbItem[] = [];
    this.collectFromRoute(this.route.root, '', collected);

    if (collected.length === 0) {
      return [];
    }

    const path = this.currentPath();
    if (path !== '/' && (collected.length === 0 || collected[0].url !== '/')) {
      collected.unshift({ labelKey: 'BREADCRUMB.HOME', url: '/' });
    }

    return this.normalizeItems(collected);
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
      const resolvedUrl = this.resolveItemUrl(item);
      const url = resolvedUrl?.replace(/\/+$/, '') || '/';
      const isHomeItem = item.labelKey === 'BREADCRUMB.HOME';
      const isCurrent = !isHomeItem && (url === path || (url === '/' && path === '/'));

      if (isLast || isCurrent) {
        return { labelKey: item.labelKey };
      }

      return { labelKey: item.labelKey, url };
    });
  }

  navigateHome(event: Event, item: BreadcrumbItem): void {
    event.preventDefault();

    const target = (this.resolveItemUrl(item) || '/').replace(/\/+$/, '') || '/';
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

  private resolveItemUrl(item: BreadcrumbItem): string | undefined {
    if (item.labelKey !== 'BREADCRUMB.HOME') {
      return item.url;
    }

    const path = this.currentPath();
    if (!path.startsWith('/admin')) {
      return item.url || '/';
    }

    if (this.auth.isSuperAdmin()) {
      return '/admin/companies';
    }

    if (this.auth.isAdmin()) {
      return '/admin/dashboard';
    }

    return item.url || '/';
  }

  private currentPath(): string {
    const path = this.router.url.split('?')[0].split('#')[0] || '/';
    return path.replace(/\/+$/, '') || '/';
  }
}
