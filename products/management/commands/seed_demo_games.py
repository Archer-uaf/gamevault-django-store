"""Create or update demo catalog data for local development."""

from datetime import date
from decimal import Decimal
from typing import Any

from django.core.management.base import BaseCommand

from products.models import Category, Product


class Command(BaseCommand):
    help = "Create or update demo categories and games for GameVault."

    CATEGORIES = (
        ("Action", "action"),
        ("RPG", "rpg"),
        ("Strategy", "strategy"),
        ("Horror", "horror"),
        ("Racing", "racing"),
        ("Indie", "indie"),
    )

    GAMES: tuple[dict[str, Any], ...] = (
        {
            "name": "Neon Drift",
            "slug": "neon-drift",
            "description": (
                "Динамичный экшен в неоновом мегаполисе, где скорость и точность "
                "решают исход каждой миссии."
            ),
            "price": Decimal("1299.00"),
            "category_slug": "action",
            "platform": Product.Platform.PC,
            "developer": "Pulse Arc Studio",
            "publisher": "GameVault Publishing",
            "release_date": date(2025, 11, 14),
            "stock": 25,
            "discount_percent": 10,
            "is_active": True,
            "is_featured": True,
        },
        {
            "name": "Mythic Realms",
            "slug": "mythic-realms",
            "description": (
                "Большая ролевая игра о древних королевствах, забытых богах и "
                "решениях, меняющих судьбу мира."
            ),
            "price": Decimal("999.00"),
            "category_slug": "rpg",
            "platform": Product.Platform.XBOX,
            "developer": "Northwind Forge",
            "publisher": "Aurora Interactive",
            "release_date": date(2024, 9, 20),
            "stock": 18,
            "discount_percent": 20,
            "is_active": True,
            "is_featured": True,
        },
        {
            "name": "Stellar Frontier",
            "slug": "stellar-frontier",
            "description": (
                "Исследуйте далёкие планеты, собирайте команду и раскройте тайну "
                "исчезнувшей космической экспедиции."
            ),
            "price": Decimal("1149.00"),
            "category_slug": "indie",
            "platform": Product.Platform.NINTENDO_SWITCH,
            "developer": "Blue Comet Games",
            "publisher": "Orbit House",
            "release_date": date(2025, 6, 6),
            "stock": 12,
            "discount_percent": 0,
            "is_active": True,
            "is_featured": True,
        },
        {
            "name": "Iron Protocol",
            "slug": "iron-protocol",
            "description": (
                "Тактический боевик о спецотряде, противостоящем автономной "
                "армии машин."
            ),
            "price": Decimal("1599.00"),
            "category_slug": "action",
            "platform": Product.Platform.PLAYSTATION,
            "developer": "Red Sector",
            "publisher": "Blackbird Digital",
            "release_date": date(2025, 3, 28),
            "stock": 9,
            "discount_percent": 0,
            "is_active": True,
            "is_featured": False,
        },
        {
            "name": "Kingdoms of Aether",
            "slug": "kingdoms-of-aether",
            "description": (
                "Стройте города на парящих островах, развивайте торговлю и "
                "защищайте королевство от воздушных флотов."
            ),
            "price": Decimal("899.00"),
            "category_slug": "strategy",
            "platform": Product.Platform.PC,
            "developer": "Skyfoundry",
            "publisher": "Maple Crown",
            "release_date": date(2023, 12, 5),
            "stock": 31,
            "discount_percent": 15,
            "is_active": True,
            "is_featured": False,
        },
        {
            "name": "Echoes in the Dark",
            "slug": "echoes-in-the-dark",
            "description": (
                "Психологический хоррор в заброшенной обсерватории, где каждый "
                "звук может оказаться предупреждением."
            ),
            "price": Decimal("749.00"),
            "category_slug": "horror",
            "platform": Product.Platform.PLAYSTATION,
            "developer": "Quiet Room",
            "publisher": "Midnight Label",
            "release_date": date(2024, 10, 31),
            "stock": 7,
            "discount_percent": 5,
            "is_active": True,
            "is_featured": False,
        },
        {
            "name": "Velocity Apex",
            "slug": "velocity-apex",
            "description": (
                "Аркадные гонки по трассам будущего с быстрыми заездами, "
                "тюнингом и глобальными таблицами лидеров."
            ),
            "price": Decimal("1099.00"),
            "category_slug": "racing",
            "platform": Product.Platform.XBOX,
            "developer": "Overtake Lab",
            "publisher": "Rapid Works",
            "release_date": date(2025, 2, 18),
            "stock": 20,
            "discount_percent": 0,
            "is_active": True,
            "is_featured": False,
        },
        {
            "name": "Pixelbound",
            "slug": "pixelbound",
            "description": (
                "Тёплое пиксельное приключение о дружбе, путешествиях и тайнах "
                "небольшого приморского города."
            ),
            "price": Decimal("399.00"),
            "category_slug": "indie",
            "platform": Product.Platform.NINTENDO_SWITCH,
            "developer": "Small Lantern",
            "publisher": "Indie Harbor",
            "release_date": date(2023, 8, 11),
            "stock": 42,
            "discount_percent": 0,
            "is_active": True,
            "is_featured": False,
        },
        {
            "name": "Ashen Crown",
            "slug": "ashen-crown",
            "description": (
                "Мрачная RPG с глубоким развитием персонажа, опасными подземельями "
                "и нелинейной историей."
            ),
            "price": Decimal("1399.00"),
            "category_slug": "rpg",
            "platform": Product.Platform.PC,
            "developer": "Grey Wolf Studio",
            "publisher": "Aurora Interactive",
            "release_date": date(2025, 1, 24),
            "stock": 14,
            "discount_percent": 25,
            "is_active": True,
            "is_featured": True,
        },
        {
            "name": "Tactical Horizon",
            "slug": "tactical-horizon",
            "description": (
                "Пошаговая стратегия о противостоянии колоний на далёкой планете "
                "с разрушаемым окружением."
            ),
            "price": Decimal("829.00"),
            "category_slug": "strategy",
            "platform": Product.Platform.PC,
            "developer": "Hexline Games",
            "publisher": "Maple Crown",
            "release_date": date(2024, 4, 16),
            "stock": 23,
            "discount_percent": 0,
            "is_active": True,
            "is_featured": False,
        },
        {
            "name": "Night Signal",
            "slug": "night-signal",
            "description": (
                "Камерный хоррор о ночном радиоведущем, который принимает сигнал "
                "из места, которого нет на карте."
            ),
            "price": Decimal("549.00"),
            "category_slug": "horror",
            "platform": Product.Platform.XBOX,
            "developer": "Static Door",
            "publisher": "Midnight Label",
            "release_date": date(2023, 10, 13),
            "stock": 0,
            "discount_percent": 30,
            "is_active": True,
            "is_featured": False,
        },
        {
            "name": "Circuit Legends",
            "slug": "circuit-legends",
            "description": (
                "Соревновательный автосимулятор с легендарными трассами, "
                "динамической погодой и детальной настройкой машин."
            ),
            "price": Decimal("1799.00"),
            "category_slug": "racing",
            "platform": Product.Platform.PLAYSTATION,
            "developer": "Gridline Motorsport",
            "publisher": "Rapid Works",
            "release_date": date(2025, 9, 12),
            "stock": 11,
            "discount_percent": 0,
            "is_active": True,
            "is_featured": True,
        },
    )

    def handle(self, *args: Any, **options: Any) -> None:
        categories: dict[str, Category] = {}
        for name, slug in self.CATEGORIES:
            category, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name},
            )
            categories[slug] = category

        created_count = 0
        updated_count = 0
        for game in self.GAMES:
            data = game.copy()
            category_slug = data.pop("category_slug")
            slug = data.pop("slug")
            data["category"] = categories[category_slug]
            _, created = Product.objects.update_or_create(
                slug=slug,
                defaults=data,
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Demo catalog ready: "
                f"{len(categories)} categories, "
                f"{created_count} games created, "
                f"{updated_count} games updated."
            )
        )
