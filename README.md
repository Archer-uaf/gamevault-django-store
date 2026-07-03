# GameVault

GameVault — учебный интернет-магазин видеоигр на Django и Django REST Framework.

На текущем этапе создан только проектный каркас: четыре Django-приложения,
PostgreSQL, Docker Compose, базовые настройки DRF/JWT/OpenAPI и инструменты проверки.
Модели предметной области, корзина, заказы, API viewsets и HTML-страницы ещё не реализованы.

## Требования

- Docker с поддержкой Docker Compose.

## Запуск

Сборка и запуск приложения и PostgreSQL:

```bash
docker compose up --build
```

Проект будет доступен по адресу <http://localhost:8000/>. На первом этапе корневой
маршрут не определён; доступны Django admin и документация API.

## Переменные окружения

Для локальных значений можно скопировать `.env.example` в `.env` и заменить секреты.
Без `.env` Docker Compose использует значения для разработки по умолчанию.

## Проверки

В запущенном окружении:

```bash
docker compose exec web python manage.py check
docker compose exec web python manage.py migrate
docker compose exec web pytest
docker compose exec web flake8
```

## Доступные служебные маршруты

- Django admin: <http://localhost:8000/admin/>
- OpenAPI schema: <http://localhost:8000/api/schema/>
- Swagger UI: <http://localhost:8000/api/docs/>

План разработки находится в [`docs/PROJECT_PLAN.md`](docs/PROJECT_PLAN.md).
