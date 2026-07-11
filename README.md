# GameVault

GameVault is an educational Django and Django REST Framework project: a digital video game store with a server-rendered storefront, a session cart, checkout, user accounts, verified-purchase reviews, JWT-protected API endpoints, and OpenAPI documentation.

The project is designed as a portfolio-ready learning project, not as a production commerce platform. It focuses on clean Django/DRF structure, realistic demo data, Ukrainian and English UI, tests, and a reproducible Docker setup.

## Portfolio snapshot

- Digital game catalog with search, category filters, platform filters, sorting, pagination, and product detail pages.
- Real-game demo catalog seeded by `seed_demo_games`, including external demo cover URLs, localized descriptions, and a static Steam UA price snapshot.
- Home page with a hot deals hero for featured games and storefront sections for genres, platforms, and recommended products.
- Session-based cart and checkout with stock validation, discounted totals, and digital key delivery wording.
- User registration, login, logout, profile editing, account dashboard, order history, and password changes.
- Reviews restricted to verified purchases.
- REST API for authentication, catalog data, cart operations, orders, and reviews.
- JWT authentication and drf-spectacular OpenAPI schema with Swagger UI.
- Ukrainian and English interface; Ukrainian source strings are translated through gettext.
- Shared order creation service for web checkout and API order creation.
- DB-level constraints for prices, discounts, stock, quantities, totals, and review ratings.
- Automated checks with pytest, flake8, mypy, Django system checks, migration checks, and OpenAPI schema validation.

## Screenshots and demo

Screenshots are not committed yet. Add portfolio captures under the following paths:

```text
docs/assets/screenshots/
  home.png
  catalog.png
  product-detail.png
  cart.png
  checkout.png
  api-schema.png
```

Recommended captures are the home hot deals hero, the filtered catalog, a product detail page with reviews, the cart and checkout flow, and Swagger UI at `/api/docs/`. Add the image links here only after the files are committed so the public README does not contain broken previews.

## Technology stack

- Python 3.12
- Django 5
- Django REST Framework
- PostgreSQL
- Docker and Docker Compose
- django-filter
- Simple JWT
- drf-spectacular
- pytest
- flake8
- mypy and django-stubs
- gettext i18n

## Quick start with Docker Compose

Requirements: Docker with Docker Compose support.

1. Copy the example environment file:

   ```powershell
   Copy-Item .env.example .env
   ```

   On macOS or Linux, use:

   ```bash
   cp .env.example .env
   ```

2. Review `.env` and replace development secrets before using the project outside a local demo environment.

3. Build and start the application with PostgreSQL:

   ```bash
   docker compose up --build
   ```

4. In another terminal, prepare the database:

   ```bash
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py createsuperuser
   ```

5. Optional: load demo game data:

   ```bash
   docker compose exec web python manage.py seed_demo_games
   ```

6. Open <http://localhost:8000/>.

## Demo seed data

Create or update the demo catalog:

```bash
docker compose exec web python manage.py seed_demo_games
```

Recreate the demo catalog from scratch:

```bash
docker compose exec web python manage.py seed_demo_games --reset
```

Warning: `seed_demo_games --reset` is a destructive local/demo operation. It deletes and recreates demo products and empty demo categories, and it can affect or be blocked by order/review data tied to demo products. Use it only on disposable local data.

The command is idempotent without `--reset`: repeated runs update demo records by slug instead of creating duplicates. Official cover files are not bundled in the repository. Seeded demo products use external Steam cover URLs for demo display, while user-provided local product images can still be uploaded through the existing image field. Demo prices are a Steam UA price snapshot collected on July 9, 2026 and are not live-synced.

## Main URLs

| Area | URL |
| --- | --- |
| Home page | <http://localhost:8000/> |
| Product catalog | <http://localhost:8000/products/> |
| Product detail | `/products/product/<slug>/` |
| Cart | <http://localhost:8000/cart/> |
| Checkout | <http://localhost:8000/checkout/> |
| User account | <http://localhost:8000/account/> |
| Django admin | <http://localhost:8000/admin/> |
| REST API root | <http://localhost:8000/api/> |
| Swagger UI | <http://localhost:8000/api/docs/> |
| OpenAPI schema | <http://localhost:8000/api/schema/> |

## REST API overview

- Authentication: `/api/auth/register/`, `/api/auth/token/`, `/api/auth/token/refresh/`, and `/api/auth/me/`.
- Catalog: read-only `/api/products/` and `/api/categories/`.
- Catalog filters: category, platform, search, price range, and ordering are documented in the schema.
- Session cart: `/api/cart/`, `/api/cart/items/`, and `/api/cart/items/<product_id>/`.
- Orders: authenticated list, detail, and create operations at `/api/orders/`.
- Reviews: public list and authenticated verified-purchase creation at `/api/reviews/`.

Use Swagger UI for complete request schemas, response schemas, filters, status codes, and authentication requirements.

## Digital order flow

GameVault models digital goods rather than boxed products. The user-facing checkout and order pages describe email-based digital key delivery, order processing, key sent, completed, and cancelled states. There is no parcel, warehouse, courier, or real payment provider integration in this educational demo.

The checkout service is shared between the web flow and API order creation, so stock validation, price calculation, order item creation, and stock decrease follow the same business rules.

## Internationalization

Ukrainian is the default interface language and English is the secondary language. Source UI strings are Ukrainian. English translations are stored in `locale/en/LC_MESSAGES/`.

Update English messages after changing UI, form, email, admin, or API-facing text:

```bash
docker compose exec web django-admin makemessages -l en --ignore=.venv/* --ignore=staticfiles/* --ignore=media/*
docker compose exec web django-admin compilemessages -l en --ignore=.venv/* --ignore=staticfiles/* --ignore=media/*
```

Check for fuzzy translations before committing:

```bash
git grep -n "fuzzy" locale/en/LC_MESSAGES/django.po
```

The storefront, admin-facing labels, email text, and API-facing descriptions should use Ukrainian or English only. Russian UI text is outside the project scope.

## Tests and quality checks

Run the main project checks in the running Docker environment:

```bash
docker compose exec web python manage.py check
docker compose exec web python manage.py makemigrations --check --dry-run
docker compose exec web pytest
docker compose exec web flake8
docker compose exec web mypy .
docker compose exec web python manage.py spectacular --validate --file /tmp/schema.yml
git diff --check
```

Useful focused checks:

```bash
docker compose exec web pytest tests/test_pages.py tests/test_i18n.py tests/test_account.py -x --tb=short
docker compose exec web pytest tests/test_api.py tests/test_checkout.py -x --tb=short
```

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

Docker Compose provides development defaults, but real secrets should be set explicitly outside local development.

## Email behavior

Order notifications use Django's email framework. The customer receives a development-safe confirmation after checkout. If `DJANGO_ADMIN_EMAIL` is set, the configured administrator also receives a new-order notification. The default development configuration uses the console email backend, so messages are printed to the web container logs and no external SMTP service is contacted.

## Admin

The Django admin supports product, category, order, review, user profile, and user management. It includes product and order actions, order count and revenue summaries, pending and paid order counts, and product review count and rating aggregates.

## Project structure

```text
config/       Django settings, root URLs, and API router
products/     Catalog models, localized descriptions, web pages, API, admin, and demo data command
orders/       Session cart, shared checkout service, orders, emails, API, and admin summaries
users/        Authentication, account dashboard, profiles, and API auth
reviews/      Verified-purchase reviews for web, API, and admin
templates/    Shared and application-specific Django templates
static/       Storefront styles, scripts, and images
locale/       English gettext translations for Ukrainian source strings
tests/        Web, API, admin, email, i18n, and business-logic tests
docs/         Project plan, contributor workflow, and final feature checklist
```

Development and verification conventions are documented in [Contributing](docs/CONTRIBUTING.md).

## Educational scope and security note

GameVault is a course project and portfolio demo, not a production commerce platform. Payment methods are mocked, no real card processing is included, the default email backend is development-only, production SMTP is not configured, external deployment is intentionally deferred, and deployment hardening such as production secrets, HTTPS, storage, monitoring, and infrastructure policy is outside the current scope.

See the [final feature checklist](docs/FEATURE_CHECKLIST.md) for the implemented and intentionally deferred scope.
