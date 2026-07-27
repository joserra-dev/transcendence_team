*This project has been created as part of the 42 curriculum by elarrea-, joscastr, luisanch, mikegonz.*

---

# Hemen-Go Camper Booking Platform

## Description

Hemen-Go is a full-stack web application for searching, reserving, managing, and validating camper parking spaces. The platform includes a public search experience, authenticated user profiles, booking history, license-plate access control, admin parking management, Stripe payments, email notifications, and multilingual support (Spanish, English, and Basque).

Key highlights (see **Features List** for ownership per feature):

- **Search & booking**: Filters, overlap validation, Stripe checkout, cancellation, and rating.
- **Users & roles**: Registration, JWT auth, profiles, friends; user, company admin, and super-admin guards.
- **Organization & analytics**: Companies CRUD, dashboards, CSV/PDF export.
- **Stripe (module of choice)**, **OCR access control**, **admin WebSocket chat**, **public API**, **i18n**, **cross-browser QA**, **Docker** deployment.

## Instructions

### Prerequisites

- **Docker** and **Docker Compose** (v2.0+)
- **Node.js** 20+ and **npm** (only if running frontend outside Docker)
- **Python** 3.12+ (only if running backend outside Docker)
- Valid SMTP credentials for email verification and password reset
- Stripe test credentials for the payment flow

**macOS:** [Colima](https://github.com/abiosoft/colima) or Docker Desktop. Recommended Colima setup: `brew install colima docker docker-compose`, then `colima start --cpu 4 --memory 8 --disk 60` (increase `--disk` if you hit “no space left” on build). Check `docker compose version` before continuing. Browsers will warn on the backend self-signed HTTPS cert at `https://localhost:8000` — accept for local dev (see **Known Limitations**).

### Environment Setup

1. Clone the repository and create the environment file:

```bash
git clone <repository-url>
cd ReadmeAdapt
make env
```

   Or copy `.env.example` to `.env` manually.

2. Edit `.env` and set at minimum:

```
POSTGRES_USER=defaultdb_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=defaultdb
DATABASE_URL=postgresql://defaultdb_user:your_secure_password@db:5432/defaultdb
JWT_SECRET_KEY=your_jwt_secret
PUBLIC_API_KEY=your_public_api_key
PUBLIC_API_RATE_LIMIT=60
STRIPE_KEY=sk_test_your_stripe_key
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=your_email@gmail.com
URL_FRONT=http://localhost:4200
URL_BACK=https://localhost:8000
```

3. Secrets must stay local and must never be committed. Use `.env.example` as reference.

### Running the Application

**Development** (recommended):

```bash
make dev
```

This runs `docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build`, starting all services.

**Production-like** (Nginx + HTTPS):

```bash
make prod
```

Dev vs prod URLs:

| Service | Dev URL | Prod URL (Nginx) |
|---------|---------|------------------|
| Frontend | http://localhost:4200 | https://localhost:443 |
| Backend API | https://localhost:8000 | https://localhost:8000 |
| Health | — | https://localhost:8000/api/status |
| PostgreSQL | localhost:5432 | (internal) |
| Redis | internal | internal |

Replace self-signed certificates and rotate `JWT_SECRET_KEY`, `PUBLIC_API_KEY`, and Stripe credentials before a real deployment.

### Stopping the Application

```bash
make clean
```

To remove all data (including the database):

```bash
make fclean
```

## Resources

### Documentation and References

- [Angular Documentation](https://angular.dev/) — SPA and admin dashboard.
- [Flask Documentation](https://flask.palletsprojects.com/) — REST API and routing.
- [Flask-JWT-Extended](https://flask-jwt-extended.readthedocs.io/), [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/), [Flask-Mailman](https://flask-mailman.readthedocs.io/)
- [Stripe](https://docs.stripe.com/), [PostgreSQL](https://www.postgresql.org/docs/), [Docker Compose](https://docs.docker.com/compose/)
- [ngx-translate](https://github.com/ngx-translate/core), [EasyOCR](https://github.com/JaidedAI/EasyOCR)

### AI Usage

AI tools (ChatGPT, GitHub Copilot, Cursor) were used during development for:

- **Requirements review**: Mapping features to the Transcendence subject and identifying compliance gaps.
- **Debugging**: Docker networking, booking overlap validation, and Stripe callback handling.
- **Code generation**: Boilerplate for Flask routes, Angular components, and SQLAlchemy models.
- **Documentation**: Structuring and drafting this README.

All AI-generated code and documentation were reviewed, tested, and understood by the team before inclusion.

## Team Information

| Member | Role | Responsibilities |
|--------|------|-----------------|
| joscastr | Product Owner, Technical Lead | Architecture, backend routes, booking logic, public API, access control, Docker/backend config, subject compliance, code reviews and integration |
| elarrea- | Developer | Backend and frontend contributions, reviews, validation, and integration |
| luisanch | Developer, QA | Super-admin and admin UI, chat and WebSockets, metrics, responsive layout, profile and user lifecycle, client booking flows, i18n (ES/EN/EU), friends system, frontend validation |
| mikegonz | Developer | Backend and frontend contributions, reviews, and validation |

## Project Management

### Work Organization

The team organized work using an informal Scrum-like approach:

- **Task distribution**: Features split by area — authentication, user profile, parking search, booking management, admin panel, public API, and DevOps.
- **Branching strategy**: Main branch with feature branches; merge conflicts resolved collaboratively.
- **Code reviews**: Backend routes and frontend flows reviewed by at least one other member before merging.
- **Regular syncs**: Progress, blockers, and next steps discussed on WhatsApp and tracked in Jira.

### Tools

- **GitHub**: Version control, pull requests, and code reviews.
- **Jira**: Task board, sprint planning, backlog, and assignment by feature area.
- **WhatsApp**, **VS Code**, **Docker Compose**, **Makefile**: Coordination and local environment.

### Communication

- Daily updates and blockers via **WhatsApp** group chat.
- Work items, priorities, and status tracked in **Jira** (tickets linked to features and PRs where applicable).
- Weekly syncs to review progress and plan the next sprint.

## Technical Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| Angular | 20.x | SPA framework for public and admin interfaces |
| TypeScript | 5.9 | Type-safe frontend development |
| Bootstrap | 5.3 | Responsive layout and UI components |
| SCSS | — | Component and layout styling |
| @ngx-translate/core | 17.x | Multilingual UI (ES, EN, EU) |
| Chart.js | 4.5 | Admin metrics visualizations |
| Socket.io-client | 4.8 | Real-time chat (admin threads) |

**Justification**: Angular + Bootstrap for structured admin UI; ngx-translate for the multilingual module.

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Flask | 3.x | REST API and server-side routing |
| Flask-SQLAlchemy | — | ORM and PostgreSQL integration |
| Flask-JWT-Extended | — | JWT authentication |
| Flask-Mailman | 1.0 | Email verification and password reset |
| Flask-Limiter | — | Rate limiting on auth and public API |
| Flask-Babel | 4.0 | Backend internationalization |
| Stripe | — | Payment processing |
| EasyOCR + OpenCV | — | License plate OCR for access control |
| WeasyPrint | — | PDF invoice generation |

**Justification**: Flask modularity, SQLAlchemy for relational data, JWT and role guards for permissions.

### Database

| Technology | Version | Purpose |
|------------|---------|---------|
| PostgreSQL | 15 | Primary relational database |

**Justification**: ACID compliance and strong support for booking overlap and the multi-tenant company model.

### Infrastructure

| Technology | Purpose |
|------------|---------|
| Docker | Containerization of all services |
| Docker Compose | Multi-service orchestration (dev and prod) |
| Nginx | HTTPS frontend hosting in production |
| Redis | Rate limiting storage for Flask-Limiter |
| Makefile | Environment generation and lifecycle commands |

**Justification**: Docker for consistent environments; Nginx for HTTPS frontend in prod; Redis for API and auth rate limits.

## Database Schema

### Models and Relationships

Horizontal read: **`Users (1) ── (1) Profiles`**; company **`admin`** profiles set `company_id` → **Company**.

```
Company (1) ──────< Profiles >────── (1) Users
   │                    │                  │  admin: profiles.company_id → Company
   ├──< Parking                               ├──< Booking
   │       └──< Space ──< Booking             └──< Friend >── Users
   │              └──< SpaceBlockedDay
   ├──< ChatMessage ── sender_id ──> Users  (thread by company_id; admin or super_admin)
   └──< InvoiceSequence
```

Admin ↔ super-admin chat only (not client **Friend** chat).

### Tables

#### Users
| Field | Type | Description |
|-------|------|-------------|
| id | BigInt (PK) | Auto-incrementing identifier |
| email | String (unique) | User email address |
| pass_user | String? | Hashed password |
| is_verified | Boolean | Email verification status |
| verification_token | String? | Email verification token |
| reset_password_token | String? | Password reset token |
| is_active | Boolean | Account active flag |

#### Profiles
| Field | Type | Description |
|-------|------|-------------|
| id | BigInt (PK) | Profile identifier |
| user_id | BigInt (FK, unique) | Linked user |
| company_id | Int? (FK) | Associated company (admins) |
| dni | String? | National ID |
| name | String | First name |
| last_name | String? | Last name |
| birth_day | Date | Birth date |
| avatar | String? | Avatar URL |
| role | Enum | `user`, `admin`, or `super_admin` |

#### Company
| Field | Type | Description |
|-------|------|-------------|
| id | Int (PK) | Company identifier |
| name | String | Company name |
| cif | String? | Tax ID |
| tbai_enabled | Boolean | TicketBAI integration flag |
| tbai_software_license | String? | TicketBAI license |

#### Parking
| Field | Type | Description |
|-------|------|-------------|
| id | BigInt (PK) | Parking identifier |
| id_company | Int (FK) | Owning company |
| name | String | Parking name |
| province / municipality | String? | Location |
| has_electricity / has_waste_disposal / has_vip_spots | Boolean? | Service flags |
| latitude / longitude | Float? | Coordinates |
| description | String? | Public description |
| tbai_serie_facturacion | String? | Invoice series |

#### Space
| Field | Type | Description |
|-------|------|-------------|
| id | BigInt (PK) | Space identifier |
| id_parking | BigInt (FK) | Parent parking |
| name | String? | Spot name |
| isvip / has_electr | Boolean? | VIP and electricity flags |
| status | String(1) | Availability status |
| price | Float? | Price per night |

#### Booking
| Field | Type | Description |
|-------|------|-------------|
| id | BigInt (PK) | Booking identifier |
| id_user | BigInt? (FK) | Booking user |
| id_space | BigInt (FK) | Reserved space |
| start_date / end_date | Date? | Stay dates |
| status | String(1) | Pending, confirmed, or processing |
| rating | Numeric? | Post-stay rating |
| license_plate | String | Vehicle plate |
| total_price | Float | Total cost |
| invoice_serie / invoice_number | String? | Invoice identifiers |
| tbai_id / tbai_qr_code | String? | TicketBAI fields |

#### Friend
| Field | Type | Description |
|-------|------|-------------|
| id | BigInt (PK) | Friendship identifier |
| user_id / friend_id | BigInt (FK) | User pair |
| created_at | DateTime | Creation timestamp |

Unique constraint: (user_id, friend_id)

#### ChatMessage
| Field | Type | Description |
|-------|------|-------------|
| id | BigInt (PK) | Message identifier |
| company_id | Int (FK) | Support thread for that company (admin ↔ super-admin) |
| sender_id | BigInt (FK) | Author: company `admin` for this `company_id`, or `super_admin` |
| content | Text | Message body |
| is_read | Boolean | Read status |
| created_at | DateTime | Sent timestamp |

## Features List

### Booking Features

| Feature | Description | Implemented by |
|---------|-------------|----------------|
| Parking search | Filter by location, dates, and amenities with pagination | joscastr, elarrea-, luisanch |
| Booking creation | Overlap validation, Stripe checkout, confirmation | joscastr, luisanch, mikegonz |
| Booking history | List, filter, cancel, rate, and view details | joscastr, luisanch |
| Invoice / TicketBAI | PDF bills and fiscal fields on payment | joscastr, mikegonz |
| Blocked days | Admin calendar blocking per space | joscastr, elarrea- |

### Payment Features

| Feature | Description | Implemented by |
|---------|-------------|----------------|
| Stripe checkout | Paid confirmation for reservations; redirects handled via `URL_FRONT` / `URL_BACK` | joscastr |

### User Features

| Feature | Description | Implemented by |
|---------|-------------|----------------|
| Registration / Login | Email/password with JWT | joscastr, elarrea- |
| Email verification | Token-based account activation | joscastr |
| Password reset | Forgot/reset flow with email | joscastr |
| User profile | View and edit profile, avatar URL | luisanch |
| Friends system | Add, list, and remove friends | luisanch |
| Multilingual UI | ES, EN, EU language switching | luisanch |
| Role-based access | User, company admin, and super-admin routes and backend guards | joscastr, luisanch |

### Real-time & Integration Features

| Feature | Description | Implemented by |
|---------|-------------|----------------|
| Admin chat (WebSocket) | Flask-SocketIO threads per company; unread counts and live messages (admin ↔ super-admin) | joscastr, luisanch, elarrea- |
| Public API | External integrations via `X-API-Key`, rate limiting, and Swagger docs | joscastr |

### Admin Features

| Feature | Description | Implemented by |
|---------|-------------|----------------|
| Parking management | CRUD for parkings and spaces | joscastr, elarrea- |
| Booking management | Admin list with date/parking/status filters, cancellation, CSV export | joscastr, luisanch |
| Analytics dashboard | Donut charts, yearly metrics, filtered exports | joscastr, luisanch |
| User administration | Super-admin CRUD for users, roles, and company assignment | joscastr |
| Company management | Super-admin companies CRUD, assign admins, metrics per enterprise | joscastr |
| Organization workflows | Link admins to companies; revoke company access and admin privileges | joscastr, luisanch |
| Admin chat | REST + WebSocket support threads per company | joscastr, elarrea-, luisanch |
| Access control (OCR) | License plate verification against active bookings (`/access-control`) | joscastr |

### Infrastructure Features

| Feature | Description | Implemented by |
|---------|-------------|----------------|
| Docker deployment | Dev and prod Compose stacks | joscastr |
| Public API | API-key + rate-limited endpoints | joscastr |
| Status endpoint | `/api/status` health check | joscastr |
| Nginx + TLS | Production frontend hosting | joscastr |
| Cross-browser QA | Manual testing on Chrome, Firefox, Safari, and Brave | luisanch |
| Privacy / Terms | `/legal/privacy` and `/legal/terms` | luisanch |

## Modules

Per the Transcendence subject (`transcendece_en.subject.pdf`): **Major = 2 points**, **Minor = 1 point**, minimum **14 points** required.

| Points | Module | Category | Type | Team member(s) | Justification |
|--------|--------|----------|------|----------------|---------------|
| 2 | Frontend + Backend Framework | Web | Major | joscastr, elarrea-, mikegonz | Angular 20 SPA + Flask REST API, containerized with Docker Compose and Makefile |
| 2 | Real-time Features (WebSockets) | Web | Major | joscastr, luisanch, elarrea- | Flask-SocketIO for admin chat: unread counts, `new_message`, and `messages_read` events |
| 2 | User Interaction | Web | Major | luisanch, joscastr, elarrea- | Admin ↔ super-admin chat, editable user profiles, and friends system between client users |
| 2 | Public API | Web | Major | joscastr | Secured `X-API-Key` access to parking/space data for external apps without sharing DB credentials or full user sessions |
| 2 | Standard User Management | User Management | Major | joscastr, luisanch, elarrea- | Registration, JWT login, profile update, avatar URL, email verification, password reset; super-admin creates users and assigns roles |
| 2 | Advanced Analytics Dashboard | Data & Analytics | Major | joscastr, luisanch | Donut charts (bookings by parking, sales by month), year filters, admin booking filters, CSV export, PDF invoices (WeasyPrint) |
| 2 | Stripe Payment (module of choice) | Modules of Choice | Major | joscastr, mikegonz | Stripe Checkout confirms paid reservations, reduces no-shows, and avoids storing card data (PCI scope) |
| 2 | Advanced Permissions | User Management | Major | joscastr, luisanch | Role-based user CRUD, `@require_admin` / `@require_super_admin`, different Angular admin views per role |
| 2 | Organization System | User Management | Major | joscastr, luisanch | Companies CRUD, assign admins to an enterprise, remove users and revoke admin privileges |
| 1 | ORM | Web | Minor | joscastr, elarrea-, mikegonz | Flask-SQLAlchemy models, migrations, and type-safe relational access to PostgreSQL |
| 1 | Advanced Search | Web | Minor | joscastr, elarrea-, luisanch | Parking search with filters, sorting, and pagination (`GET /api/parking/search`) |
| 1 | Multiple Languages | Accessibility & i18n | Minor | luisanch | Three languages (ES, EN, EU) on Angular (`@ngx-translate/core`) and backend emails/messages (Flask-Babel) |
| 1 | Support for Additional Browsers | Web | Minor | luisanch | Full manual QA on Chrome plus Firefox, Safari, and Brave (≥2 additional browsers beyond baseline) |

**Total: 22 points** (18 Major + 4 Minor; 14 required). Subject bonus beyond 14 pts is capped at **+5** in evaluation.

### Stripe Payment — module of choice (subject IV.10)

We chose **Stripe Checkout** as our custom **Major** module because camper reservations need reliable online payment before a spot is confirmed.

- **Why this module**: Without payment at booking time, spaces stay blocked by abandoned flows; Stripe matches our B2C model without in-house card storage (PCI).
- **Technical challenge**: Redirect flow (session → pay on Stripe → confirm/cancel callbacks), booking status transitions, secrets in `.env` across Docker dev/prod.
- **Value to Hemen-Go**: Confirmed bookings drive metrics, invoices (TicketBAI), and plate access; reduces no-shows vs unpaid holds.
- **Why Major (2 pts)**: Backend session creation, confirm routes, frontend booking flow, and error handling — comparable scope to other Majors.

### Module Implementation Details

| Points | Module | Type | Implementation |
|--------|--------|------|----------------|
| 2 | Frontend + Backend Framework | Major | Angular 20 (public, client, admin, auth); Flask blueprints; Docker dev/prod via Makefile |
| 2 | Real-time Features (WebSockets) | Major | Flask-SocketIO, JWT on connect, company rooms, live chat and unread badge updates |
| 2 | User Interaction | Major | REST + WebSocket admin chat; profile `/api/users/update`; friends `/api/friends` |
| 2 | Public API | Major | `/api/public/*`, `X-API-Key`, Redis rate limit, Swagger (Flasgger), parking/space endpoints |
| 2 | Standard User Management | Major | Register, login, `/me`, avatar URL on profile; super-admin `POST /api/admin/users` with role and `companyId` |
| 2 | Advanced Analytics Dashboard | Major | `/api/admin/metrics`, donut charts, year filter; admin booking filters; CSV export; PDF `/api/booking/<id>/bill` |
| 2 | Stripe Payment | Major | Checkout on booking create, confirm/cancel callbacks, status update after payment |
| 2 | Advanced Permissions | Major | `UserRole` user/admin/super_admin; route guards; super-admin-only user management |
| 2 | Organization System | Major | Company CRUD; `Profiles.company_id`; remove user from company and revoke admin role |
| 1 | ORM | Minor | Flask-SQLAlchemy; models in `backend/area_backend/models/`; PostgreSQL schema and migrations |
| 1 | Advanced Search | Minor | Filters (location, dates, amenities), sorting, pagination on `/api/parking/search` and public search UI |
| 1 | Multiple Languages | Minor | `frontend/camper/src/assets/i18n/{es,en,eu}.json`; Flask-Babel for backend/email translations |
| 1 | Support for Additional Browsers | Minor | Angular SPA tested on Chrome, Firefox, Safari, and Brave (layout, auth, booking, admin flows) |

## Known Limitations

- **Development TLS**: Self-signed HTTPS in Docker; Angular dev on HTTP (`make dev`); production-like HTTPS via Nginx (`make prod`).
- **Avatar**: Profiles store an **avatar URL**, not server-side file upload.
- **Friends**: List implemented; **online status** for friends is not implemented.
- **Access control (OCR)**: Depends on camera quality and lighting; verification page needs API key and parking context in production.
- **Email**: Verification and password reset require working SMTP in `.env`.
- **Stripe / Public API**: Test Stripe keys by default; rotate `PUBLIC_API_KEY` and use live Stripe only with valid TLS in production.
- **Evaluation scope**: Module points exceed the 14-point minimum; subject counts **+5 bonus max** beyond those 14.

## Individual Contributions

### joscastr

**Primary areas**: Product Owner, Technical Lead — backend architecture, booking and search, auth and session security, public/admin API, access control, Docker/HTTPS, subject compliance

- **Booking and search**: Parking availability by date range in `Parking.to_dict()` and `GET /api/parking/search` with filters, pagination, and sorting
- **Booking API**: End-to-end `/api/booking` (create with Stripe Checkout, confirm/cancel callbacks, detail, history, cancel, rate, QR, PDF bill) with space overlap and same-user date overlap rules
- **License plate and pricing**: Plate-based duplicate rules, stay-day calculation aligned between client and admin, cancel allowed only before the stay starts (user and admin routes)
- **Profile and auth**: Full `/me` serialization and `PUT /api/users/update`; login returns complete user payload for the client app
- **Route security**: `authGuard` and `adminGuard`; JWT expiry check in `isLoggedIn()`; HTTP 401 interceptor clears session and redirects on token expiry
- **Public and admin API**: `X-API-Key` public routes with rate limiting; admin parking/space CRUD; companies and user management endpoints; `GET /api/status` health check
- **Friends and legal**: Friends API (`GET/POST/DELETE /api/friends`); legal pages `/legal/privacy` and `/legal/terms` with correct route param handling when switching pages
- **Access control**: License-plate OCR verification route and verification page, protected with the public API key in production
- **Dates and i18n hygiene**: Fixed `startDate` serialization typo; timezone-safe date defaults; history filter (`estado` vs `status`); unified `startDate`/`endDate` across Angular and Flask; ES/EN/EU keys for search and booking errors (e.g. parking not found)
- **Stripe and payments**: Checkout session creation; success/cancel URLs from `URL_FRONT`/`URL_BACK`; booking status transitions after payment; production checklist for `STRIPE_KEY` and public redirect URLs
- **DevOps**: Flask blueprints and role decorators; Docker Compose dev/prod; backend HTTPS in Docker; Nginx HTTPS frontend; `Makefile` (`make env`, `make dev`, `make prod`); CORS restricted to frontend origin; Docker healthcheck via `/api/status`; `BookingStatus` constants; structured logging instead of debug prints
- **Subject compliance**: README structure, module point mapping, and coordination of gaps against `transcendece_en.subject.pdf`
- Manual validation and integration testing on booking, search, profile/auth guards, and admin endpoints; aligned Angular services with HTTPS backend URLs in Docker
- **Challenges overcome:** Partial booking overlaps and same-user double bookings → SQL overlap rules and status constants; Stripe/HTTPS in Compose → env URLs and Nginx proxy to TLS backend; JWT “zombie” sessions → guards plus 401 logout; production boot crash from `current_app` at import → module-level logging fix; feature-branch drift on `develop` → frequent syncs and review before merge

### elarrea-

**Primary areas**: Full-stack development, integration, reviews

- Backend and frontend work on parking search, parking/space management, and blocked-day calendar flows
- Contributed to registration/login flows, admin chat (REST/WebSocket integration), and booking list behaviour
- Implemented and reviewed overlap validation behaviour with the team on search and booking paths
- Supported public API and admin parking endpoints during integration and manual testing
- Resolved merge conflicts and cross-branch integration on `develop` (parking, chat, and admin panels)
- **Challenges overcome:** Large feature branches and merge conflicts → smaller PRs, paired reviews, and shared testing on parking and chat flows.

### luisanch

**Primary areas**: Full-stack frontend focus — super-admin/admin UI, chat, metrics, responsive layout, profile, user lifecycle, client flows, i18n, QA

- Built super-admin vs company-admin separation (`/admin/companies`, `manage-companies`, `company-parkings`, guards and redirects)
- Admin bookings panel: filters, pagination, cancellation UI, CSV export, and related translations
- Unified admin login, reusable `confirm-dialog`, destructive-action modals, DELETE user/spot endpoints
- Parking form: latitude, longitude, description fields and backend mapping; admin parking/space CRUD UI
- Company metrics: CSS donut charts wired to `/api/admin/metrics`; dashboard parking filters and export flows
- Differentiated admin/user welcome emails and role-based dashboard entry points
- Admin ↔ super-admin chat (REST then WebSocket), unread badges, role-colored alerts, chat layout, Flask-SocketIO, Docker/nginx WebSocket proxy, dynamic metric years
- Contextual admin «Home» and logo links in `breadcrumb` and `header` for admin vs super-admin
- Profile flow: editable DNI when empty, document validator, styled alerts, avatar URL mapping; friends system UI (add/list/remove)
- Global responsive adaptation (SCSS/HTML mixins, mobile user cards, admin toolbars, chat and calendar layouts)
- Admin calendar per **space** (`SpaceBlockedDay`), parking/space selectors, blocked days, public search date picker fix (Firefox)
- Booking cancel UI aligned with backend rules; admin user delete with FK handling; customer snapshot; logical delete via `is_active`
- Angular client flows: search, booking, history, profile; ES / EN / EU translations; Privacy Policy and Terms of Service pages
- Cross-browser manual QA (Chrome, Firefox, Safari, Brave) on auth, booking, admin, and chat flows
- Frontend form validation, peer reviews, and integration with backend API changes
- **Challenges overcome:** SocketIO behind Nginx/Docker → WebSocket proxy settings and JWT on connect; admin UI on mobile → responsive SCSS refactors and cross-browser QA.

### mikegonz

**Primary areas**: Booking and parking routes, PDF invoices, emails, frontend polish

- PDF invoice generation (WeasyPrint) and bill templates with multilingual support; invoice fields linked to booking payment data
- Backend updates to `booking_routes.py` and `parking_routes.py` (booking creation, listing, and parking detail behaviour)
- Email service adjustments, templates, and tests for verification and transactional mail
- Parking and profile form UX: required-field highlighting, save feedback messaging, and validation messages
- Supported TicketBAI / invoice metadata on paid bookings together with the booking flow
- Refactors and merge integration on `develop`; code reviews on backend routes and frontend booking/parking screens
- **Challenges overcome:** Multilingual PDF invoices → WeasyPrint templates coordinated with Flask-Babel locales and booking payment data.
