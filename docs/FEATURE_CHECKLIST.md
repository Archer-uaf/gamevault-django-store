# GameVault final feature checklist

## Implemented

- [x] Django project with PostgreSQL and Docker Compose.
- [x] Product and category catalog with search, filtering, sorting, pagination, and product detail pages.
- [x] Platform support in the web catalog and API product catalog.
- [x] Real-game demo catalog seeded by `seed_demo_games`.
- [x] Demo product covers via external cover URLs; official cover files are not bundled.
- [x] Static Steam UA price snapshot for demo products; no runtime Steam sync.
- [x] Localized product descriptions with Ukrainian source text and English demo text.
- [x] Home hot deals hero, popular genres, platform cards, and recommended products.
- [x] Ukrainian and English i18n with Ukrainian as the default language.
- [x] Session-based web cart and session-backed API cart.
- [x] Checkout with stock validation, atomic order creation, discounted totals, and digital key delivery wording.
- [x] Shared order creation service used by web checkout and API order creation.
- [x] Development-safe customer confirmations and optional administrator notifications.
- [x] Registration, authentication, digital profile editing, dashboard, order history, and password changes.
- [x] Verified-purchase reviews in the web interface and REST API.
- [x] REST API for catalog data, cart operations, orders, and reviews.
- [x] JWT registration, token, refresh, and current-user endpoints.
- [x] Swagger UI and validated OpenAPI schema.
- [x] DB-level constraints for product price, discount, stock, order totals, order item price/quantity, and review rating.
- [x] Django admin actions, order/revenue/status summaries, and product review aggregates.
- [x] Automated tests plus Django system checks, migration checks, flake8, mypy, and schema validation.

## Intentionally mocked or deferred

- [x] Payments use mock methods; no real payment provider or card processing is included.
- [x] Email uses Django's console backend by default; production SMTP is not configured.
- [x] Digital key delivery is represented through order status and notification wording; no external key provider is integrated.
- [x] GraphQL, Celery, Redis, and SPA frontend rewrites are outside the project scope.
- [x] External hosting, production deployment, and infrastructure hardening are deferred.
