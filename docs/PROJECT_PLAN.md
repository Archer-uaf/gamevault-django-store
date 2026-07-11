# GameVault project plan

GameVault was developed as a staged educational Django/DRF digital game store. The stages below describe the completed roadmap and the boundaries used during implementation.

## Completed stages

1. Project foundation: Django project, application layout, Docker Compose, PostgreSQL, environment configuration, and quality tooling.
2. Catalog domain: categories, products, platforms, prices, discounts, stock, product images, cover URLs, indexes, validators, and DB constraints.
3. Django admin: product, category, order, review, profile, and user management.
4. Storefront catalog: list page, search, filters, platform filter, sorting, pagination, and product detail pages.
5. Demo catalog: real-game seed data, localized descriptions, external cover URLs, Steam UA price snapshot, genre/platform sections, and hot deals hero.
6. Session cart: add, update, remove, totals, discounts, and stock validation.
7. Checkout and orders: shared order creation service, atomic stock decrease, digital key delivery wording, user feedback, and order history.
8. Account area: registration, login, logout, profile editing, dashboard, order history, and password changes.
9. Reviews: verified-purchase review policy in web and API flows.
10. REST API: product/category endpoints, cart endpoints, order endpoints, review endpoints, permissions, filtering, and JWT authentication.
11. OpenAPI: drf-spectacular schema and Swagger UI.
12. Internationalization: Ukrainian source UI and English gettext translations.
13. Tests and quality: pytest coverage for core flows, flake8, mypy, Django checks, migration checks, and schema validation.
14. Documentation: README, feature checklist, and workflow notes.

## Current project scope

Implemented:

- Digital video game storefront.
- Web catalog, cart, checkout, account, orders, and reviews.
- REST API with JWT and OpenAPI documentation.
- PostgreSQL/Docker development setup.
- Demo catalog suitable for portfolio screenshots.
- Quality checks suitable for an educational Django/DRF project.

Intentionally deferred:

- Real payment gateway integration.
- Production SMTP setup.
- External hosting and production infrastructure.
- Advanced fulfillment automation.
- GraphQL, background workers, Redis, and frontend SPA rewrites.

## Planning principles

- Keep each change small and testable.
- Model changes include migrations.
- Business rules live in services or models rather than templates.
- Shared behavior between web and API flows should not be duplicated.
- Public documentation should describe implemented behavior only.
- UI text should remain Ukrainian and English, with Ukrainian source strings.
