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
                "Динамічний екшн у неоновому мегаполісі, де швидкість і точність "
                "вирішують результат кожної місії."
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
                "Велика рольова гра про стародавні королівства, забутих богів і "
                "рішення, що змінюють долю світу."
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
                "Досліджуйте далекі планети, збирайте команду та розкрийте таємницю "
                "зниклої космічної експедиції."
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
                "Тактичний бойовик про спецзагін, що протистоїть автономній "
                "армії машин."
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
                "Будуйте міста на летючих островах, розвивайте торгівлю та "
                "захищайте королівство від повітряних флотів."
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
                "Психологічний горор у покинутій обсерваторії, де кожен "
                "звук може виявитися попередженням."
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
                "Аркадні перегони трасами майбутнього зі швидкими заїздами, "
                "тюнінгом і глобальними таблицями лідерів."
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
                "Тепла піксельна пригода про дружбу, подорожі й таємниці "
                "невеликого приморського міста."
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
                "Похмура RPG із глибоким розвитком персонажа, небезпечними "
                "підземеллями "
                "та нелінійною історією."
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
                "Покрокова стратегія про протистояння колоній на далекій планеті "
                "з руйнівним оточенням."
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
                "Камерний горор про нічного радіоведучого, який приймає сигнал "
                "із місця, якого немає на карті."
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
                "Змагальний автосимулятор із легендарними трасами, "
                "динамічною погодою та детальним налаштуванням машин."
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
