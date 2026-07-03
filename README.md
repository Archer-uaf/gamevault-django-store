# GameVault

GameVault — учебный интернет-магазин видеоигр на Django и Django REST Framework.

В проекте настроены четыре Django-приложения, PostgreSQL, Docker Compose,
DRF/JWT/OpenAPI и инструменты проверки. Реализованы базовые доменные модели каталога,
заказов, профилей пользователей и отзывов, а также их Django admin-конфигурация.
Подключены главная страница, каталог с поиском/фильтрами/сортировкой/пагинацией и
детальная страница игры на Django templates. Реализована корзина на Django sessions
с проверкой остатков и управлением количеством. Checkout, auth views, создание
отзывов и API viewsets ещё не реализованы.

## Визуальная тема

HTML/CSS-шаблон [Hop-and-Barley](https://github.com/MagicCodeGit/Hop-and-Barley),
указанный в техническом задании, использован как визуальная основа. Структура,
цветовая тема и контент адаптированы под магазин видеоигр GameVault; клиентская
имитация авторизации и бизнес-логика исходного шаблона не переносились.

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

Проект будет доступен по адресу <http://localhost:8000/>. Корневой маршрут открывает
статическую главную страницу GameVault; также доступны Django admin и документация API.

## Переменные окружения

Для локальных значений можно скопировать `.env.example` в `.env` и заменить секреты.
Без `.env` Docker Compose использует значения для разработки по умолчанию.

## Демо-каталог

После применения миграций можно создать или обновить 6 категорий и 12 демо-игр:

```bash
docker compose exec web python manage.py seed_demo_games
```

Команда идемпотентна: повторный запуск обновляет существующие записи по slug и не
создаёт дубликаты.

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

- Главная страница: <http://localhost:8000/>
- Каталог игр: <http://localhost:8000/products/>
- Страница игры: `http://localhost:8000/product/<slug>/`
- Корзина: <http://localhost:8000/cart/>
- Django admin: <http://localhost:8000/admin/>
- OpenAPI schema: <http://localhost:8000/api/schema/>
- Swagger UI: <http://localhost:8000/api/docs/>

План разработки находится в [`docs/PROJECT_PLAN.md`](docs/PROJECT_PLAN.md).
