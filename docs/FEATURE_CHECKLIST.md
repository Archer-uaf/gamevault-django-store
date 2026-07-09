# GameVault final feature checklist

## Implemented

- [x] Django project with PostgreSQL and Docker Compose.
- [x] Product and category catalog with search, filtering, sorting, and pagination.
- [x] Product detail pages with stock, discounts, and review display.
- [x] Realistic demo catalog with real game titles, genre links, and external demo cover URLs.
- [x] Ukrainian and English i18n with Ukrainian as the default language.
- [x] Session-based web cart and session-backed API cart.
- [x] Checkout with stock validation, atomic order creation, and mock payment methods.
- [x] Development-safe customer confirmations and optional administrator notifications.
- [x] Registration, authentication, digital profile editing, dashboard, order history, and password changes.
- [x] Verified-purchase reviews in the web interface and REST API.
- [x] REST API for catalog data, cart operations, orders, and reviews.
- [x] JWT registration, token, refresh, and current-user endpoints.
- [x] Swagger UI and validated OpenAPI schema.
- [x] Django admin actions, order/revenue/status summaries, and product review aggregates.
- [x] Automated tests plus flake8, mypy, migration, and schema checks.

## Intentionally mocked or deferred

- [x] Payments use mock methods; no real payment provider or card processing is included.
- [x] Official cover image files are not bundled; seeded demo covers use external URLs and CSS fallback remains available.
- [x] Email uses Django's console backend by default; production SMTP is not configured.
- [x] GraphQL is outside the project scope.
- [x] External hosting, production deployment, and infrastructure hardening are deferred.
