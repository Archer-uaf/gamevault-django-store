# GameVault

GameVault is an educational video game store built with Django and Django REST Framework. It combines a server-rendered storefront, a session-backed shopping cart and checkout, user accounts, verified-purchase reviews, a JWT-protected REST API, and an extended Django admin.

## Technology stack

- Python 3.12
- Django 5
- Django REST Framework
- PostgreSQL
- Docker and Docker Compose
- pytest, flake8, mypy, and django-stubs
- drf-spectacular for OpenAPI and Swagger UI

## Features

- Product catalog with search, filters, sorting, pagination, and product details
- Realistic demo game catalog with external demo cover URLs and localized descriptions
- Ukrainian and English storefront, with Ukrainian as the default language
- Session-based cart with stock validation and discounted totals
- Guest checkout with mock payment methods and order confirmation
- Development-safe customer confirmations and optional administrator notifications
- Registration, login, logout, profile editing, dashboard, order history, and password changes
- Reviews restricted to verified purchases
- REST API for authentication, catalog data, cart operations, orders, and reviews
- JWT authentication and interactive Swagger/OpenAPI documentation
- Admin management, bulk actions, and dashboard analytics

## Quick start with Docker Compose

Requirements: Docker with Docker Compose support.

1. Copy the example environment file:

   ```powershell
   Copy-Item .env.example .env
   ```

   On macOS or Linux, use `cp .env.example .env`.

2. Review `.env` and replace the development secrets.

3. Build and start the application and PostgreSQL:

   ```bash
   docker compose up --build
   ```

4. In another terminal, prepare the database and optional demo content:

   ```bash
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py createsuperuser
   docker compose exec web python manage.py seed_demo_games --reset
   ```

5. Open <http://localhost:8000/>.

The demo seed command is idempotent: repeated runs update records by slug instead of creating duplicates. With `--reset`, it replaces previous demo titles with a real-game demo catalog. Official cover files are not bundled in the repository; seeded demo products use external Steam cover URLs for display, while user-provided local product images can still be uploaded through the existing image field.

## Environment variables

The checked-in `.env.example` documents the settings used by the Docker development environment:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_DEFAULT_FROM_EMAIL`
- `DJANGO_ADMIN_EMAIL`
- `DJANGO_EMAIL_BACKEND`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`

Docker Compose provides development defaults, but real secrets should always be set explicitly outside local development.

## Main URLs

| Area | URL |
| --- | --- |
| Home page | <http://localhost:8000/> |
| Product catalog | <http://localhost:8000/products/> |
| Product detail | `/products/product/<slug>/` |
| Shopping cart | <http://localhost:8000/cart/> |
| Checkout | <http://localhost:8000/checkout/> |
| User account | <http://localhost:8000/account/> |
| Django admin | <http://localhost:8000/admin/> |
| REST API root | <http://localhost:8000/api/> |
| Swagger UI | <http://localhost:8000/api/docs/> |
| OpenAPI schema | <http://localhost:8000/api/schema/> |

## REST API overview

- Authentication: `/api/auth/register/`, `/api/auth/token/`, `/api/auth/token/refresh/`, and `/api/auth/me/`
- Catalog: read-only `/api/products/` and `/api/categories/`
- Session cart: `/api/cart/`, `/api/cart/items/`, and `/api/cart/items/<product_id>/`
- Orders: authenticated list, detail, and create operations at `/api/orders/`
- Reviews: public list and authenticated verified-purchase creation at `/api/reviews/`

Use Swagger UI for the complete request schemas, response schemas, filters, and authentication requirements.

## Internationalization

Ukrainian is the default interface language and English is the secondary language. Web, admin, email, and API-facing text uses Ukrainian or English; Russian is not used in the application interface.

English translations are stored under `locale/en/LC_MESSAGES/` and can be rebuilt with:

```bash
docker compose exec web django-admin compilemessages -l en
```

## Email behavior

Order notifications use Django's email framework. The customer receives a confirmation after checkout. If `DJANGO_ADMIN_EMAIL` is set, the configured administrator also receives a new-order notification. The default development configuration uses the console email backend, so messages are printed to the web container logs and no external SMTP service is contacted. The sender and backend are configured through `DJANGO_DEFAULT_FROM_EMAIL` and `DJANGO_EMAIL_BACKEND`.

## Admin

The Django admin supports product, category, order, review, user profile, and user management. It includes order and product actions, order count and revenue summaries, pending and paid order counts, and product review count and rating aggregates.

## Tests and quality checks

Run the complete project checks in the running Docker environment:

```bash
docker compose exec web python manage.py check
docker compose exec web python manage.py makemigrations --check --dry-run
docker compose exec web pytest
docker compose exec web flake8
docker compose exec web mypy .
docker compose exec web python manage.py spectacular --validate --file /tmp/schema.yml
git diff --check
```

## Project structure

```text
config/       Django settings, root URLs, and API router
products/     Catalog models, localized descriptions, web pages, API, admin, and demo data command
orders/       Session cart, checkout, orders, emails, API, and admin analytics
users/        Authentication, account dashboard, profiles, and API auth
reviews/      Verified-purchase reviews for web, API, and admin
templates/    Shared and application-specific Django templates
static/       Storefront styles, scripts, and images
locale/       English gettext translations for Ukrainian source strings
tests/        Web, API, admin, email, i18n, and business-logic tests
docs/         Project plan, workflow notes, and final feature checklist
```

## Educational scope

GameVault is a course project, not a production commerce platform. Payment methods are intentionally mocked: no real payment gateway or card processing is included. The default email backend is development-only, production SMTP is not configured, GraphQL is not included, and external deployment is intentionally deferred.

See the [final feature checklist](docs/FEATURE_CHECKLIST.md) for the implemented and intentionally deferred scope.
