import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, NavigationEnd, Router, RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { filter, map, merge, of, startWith } from 'rxjs';
import { toSignal } from '@angular/core/rxjs-interop';

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
      const url = item.url?.replace(/\/+$/, '') || '/';
      const isCurrent = url === path || (url === '/' && path === '/');

      if (isLast || isCurrent) {
        return { labelKey: item.labelKey };
      }

      return { labelKey: item.labelKey, url };
    });
  }

  private currentPath(): string {
    const path = this.router.url.split('?')[0].split('#')[0] || '/';
    return path.replace(/\/+$/, '') || '/';
  }
}
