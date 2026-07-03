# GameVault

GameVault — учебный интернет-магазин видеоигр на Django и Django REST Framework.

В проекте настроены четыре Django-приложения, PostgreSQL, Docker Compose,
DRF/JWT/OpenAPI и инструменты проверки. Реализованы базовые доменные модели каталога,
заказов, профилей пользователей и отзывов, а также их Django admin-конфигурация.
Корзина, checkout, API viewsets и HTML-страницы ещё не реализованы.

## Доменные модели

- `Category` и `Product` — категории и видеоигры каталога.
- `UserProfile` — контактные данные пользователя.
- `Order` и `OrderItem` — заказ и снимки его товарных позиций.
- `Review` — оценка и комментарий пользователя к товару.

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
docker compose exec web mypy .
```

## Доступные служебные маршруты

- Django admin: <http://localhost:8000/admin/>
- OpenAPI schema: <http://localhost:8000/api/schema/>
- Swagger UI: <http://localhost:8000/api/docs/>

План разработки находится в [`docs/PROJECT_PLAN.md`](docs/PROJECT_PLAN.md).
