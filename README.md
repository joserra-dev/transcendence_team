*This project has been created as part of the 42 curriculum by the transcendence_team.*

# Hemen-Go Camper Booking Platform

## Description

Hemen-Go is a full-stack web application for searching, reserving, managing, and validating camper parking spaces. The application includes a public search experience, authenticated user profiles, booking history, QR/plate access control, admin parking management, email notifications, and multilingual support.

Key features:
- Public parking search with filters by location, dates, electricity, waste disposal, and VIP spots.
- Authenticated booking flow with overlap validation for spaces and users.
- User profile management, password reset, email verification, and payment method configuration.
- Admin dashboard to create, update, and manage parkings and spaces.
- Booking history, cancellation, rating, QR code endpoint, and license plate access verification.
- English, Spanish, and Basque translations.
- Docker Compose environment for local development.

## Instructions

### Prerequisites

- Node.js 20+ and npm
- Python 3.12+
- Docker and Docker Compose
- PostgreSQL-compatible environment for production deployment
- A valid deployment domain and TLS certificates for HTTPS

### Local development

1. Clone the repository.
2. Copy `.env.example` to `.env` and fill in real local values.
3. Start the stack:

```bash
docker compose up --build
```

4. Open the frontend at the `URL_FRONT` value defined in `.env`, usually `http://localhost:4200`.

### Environment variables

The application reads configuration from `.env`. Secrets must stay local and must never be committed.

Important variables:
- `DATABASE_URL`: PostgreSQL connection string.
- `JWT_SECRET_KEY`: secret used to sign JWT tokens.
- `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER`: email service credentials.
- `PUBLIC_API_KEY`: API key for the documented public API.
- `PUBLIC_API_RATE_LIMIT`: requests per minute per IP for the public API.

Use `.env.example` as the template.

## Resources

Relevant documentation:
- Angular documentation: https://angular.dev/
- Flask documentation: https://flask.palletsprojects.com/
- Flask-JWT-Extended documentation: https://flask-jwt-extended.readthedocs.io/
- Flask-SQLAlchemy documentation: https://flask-sqlalchemy.palletsprojects.com/
- Docker Compose documentation: https://docs.docker.com/compose/

### AI usage

AI tools were used to review requirements, identify compliance gaps, refactor repetitive code, generate documentation drafts, and suggest tests. All generated code and documentation were reviewed against the project architecture and the `transcendence_en.subject.pdf` requirements before being accepted.

## Team Information

| Member | Roles | Responsibilities |
| --- | --- | --- |
| joserra-dev | Product Owner, Technical Lead, Developer | Product scope, architecture decisions, backend routes, booking logic, subject compliance review |
| luis | Developer, QA | Frontend features, styling, component validation, testing support |
| Additional teammates | Developers | Backend/frontend contributions, reviews, and validation |

If the team composition changed during the project, each member must update this table honestly before submission.

## Project Management

The team organized work through Git branches, pull requests, and local code reviews. Main coordination happened through Discord and shared notes. Features were split by area: authentication, user profile, parking search, booking management, admin panel, and DevOps.

Recommended practices followed:
- Feature branches for isolated work.
- Peer review for backend routes and frontend flows.
- Shared notes for decisions and known issues.
- Docker Compose as the default local environment.

## Technical Stack

- Frontend: Angular 20, TypeScript, Bootstrap, SCSS, `@ngx-translate/core`
- Backend: Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-Mailman, SQLAlchemy ORM
- Database: PostgreSQL
- DevOps: Docker, Docker Compose, Nginx for frontend static hosting
- Security: password hashing with Werkzeug, JWT authentication, backend validation, public API key and rate limiting
- AI/OCR: EasyOCR and OpenCV for license plate verification

## Database Schema

Main tables:
- `users`: authentication identity, email, password hash, verification and password reset tokens.
- `profiles`: personal profile, role, company relation, DNI, birth date, payment method, IBAN, card token/last digits.
- `company`: organization owning parkings and administrators.
- `parking`: parking location, services, description, coordinates, TicketBAI series.
- `space`: parking spot, price, VIP/electricity flags, status.
- `booking`: user booking with space, dates, status, rating, license plate, total price, invoice/TicketBAI fields.
- `invoice_sequence`: invoice numbering support per company.

Main relationships:
- `users` 1:1 `profiles`
- `company` 1:N `profiles`
- `company` 1:N `parking`
- `parking` 1:N `space`
- `users` 1:N `booking`
- `space` 1:N `booking`

## Features List

| Feature | Team member(s) | Description |
| --- | --- | --- |
| Parking search | Backend/frontend team | Filters parkings by location, dates, and amenities. |
| Booking creation | Backend/frontend team | Creates reservations and prevents overlapping bookings. |
| User authentication | Backend/frontend team | Registration, login, email verification, password reset. |
| User profile | Backend/frontend team | Profile update, password change, payment method configuration. |
| Booking history | Backend/frontend team | List, filter, cancel, rate, and view booking details. |
| Admin panel | Backend/frontend team | Manage parkings and spaces for authorized administrators. |
| Access control | Backend team | OCR license plate verification against active bookings. |
| Public API | Backend team | API-key protected and rate-limited public endpoints. |
| Status endpoint | Backend team | `/api/status` health check for DevOps validation. |
| Multilingual UI | Frontend team | Spanish, English, and Basque translations. |

## Modules

| Module | Type | Points | Justification |
| --- | --- | --- | --- |
| Web: frontend and backend frameworks | Major | 2 | Angular frontend and Flask backend. |
| Web: ORM | Minor | 1 | Flask-SQLAlchemy models and relationships. |
| User Management: standard user management | Major | 2 | Registration, login, profile update, avatar-ready profile model, password reset, email verification. |
| User Management: advanced permissions | Major | 2 | User, admin, and super-admin roles with guarded routes and backend checks. |
| Accessibility and Internationalization: multiple languages | Minor | 1 | ES, EN, EU translations with language switching. |
| Web: advanced search | Minor | 1 | Search by location, dates, electricity, waste disposal, and VIP spots. |
| Web: notification system | Minor | 1 | Email verification, password recovery, and booking email templates. |
| DevOps: health check/status | Minor | 1 | `/api/status` endpoint and Docker Compose database health check. |
| Modules of choice: booking/access system | Major | 2 | Custom reservation system with QR endpoint, booking history, cancellation, rating, and OCR access verification. |
| Modules of choice: public API | Minor | 1 | Secured public API with API key, rate limiting, and documented CRUD-style endpoints. |

Total: 14 points.

## Individual Contributions

### joserra-dev
- Backend architecture, Flask routes, models, booking validation, admin API, public API, status endpoint, access-control OCR route.
- Docker/backend configuration and subject compliance review.

### luis
- Angular components, styling, booking UI, history/profile/admin flows, translations, frontend validation.

### Additional teammates
- Contributions, reviews, and validation should be documented here before submission.

## Known Limitations

- Local Docker Compose uses HTTP for development. Production must be deployed behind HTTPS with valid certificates.
- The public API key is stored in `.env` and must be rotated before any real deployment.
- Email credentials are local development secrets and must not be committed.
- Some UI labels and tests still need final peer review before submission.

## Privacy Policy and Terms of Service

The application includes accessible links in the footer:
- `/legal/privacy`
- `/legal/terms`

Both pages are translated and contain project-specific content.
