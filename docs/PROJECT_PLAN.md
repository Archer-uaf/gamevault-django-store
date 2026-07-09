# GameVault project plan

The project is developed in small stages. Each stage is implemented and verified separately.

## Stage 1. Project foundation

- Django project `config`.
- Applications `products`, `orders`, `users`, and `reviews`.
- PostgreSQL, Docker Compose, and environment variables.
- Base DRF, JWT, django-filter, and drf-spectacular configuration.
- pytest, flake8, and mypy tooling.
- Operational documentation.

Stage result: the project starts, system checks pass, and standard migrations apply. Domain models and business logic are outside this stage.

## Later stages

1. Catalog models and migrations.
2. Django admin setup.
3. Catalog list, search, filtering, sorting, and pagination.
4. Video game detail page.
5. Django session cart.
6. Checkout, order creation, and transactional stock decrease.
7. Registration, profile, and order history.
8. Reviews and ratings.
9. REST API and permissions.
10. JWT and OpenAPI documentation.
11. Broader tests, linting, and typing.
12. README finalization and build verification.

## Planning principles

- One stage should not silently implement the next stage.
- Model changes always include migrations.
- Business logic includes a minimal set of tests.
- Startup, structure, and public API changes are reflected in documentation.
- One local commit is acceptable after a completed logical stage.
