"""Create or update realistic demo catalog data for local development."""

from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand

from products.models import Category, Product

DEMO_COVER_DIR = "demo/covers"


def demo_cover_path(filename: str) -> str:
    """Return a media-relative cover path when the local placeholder exists."""
    media_path = Path(settings.MEDIA_ROOT) / DEMO_COVER_DIR / filename
    if media_path.exists():
        return f"{DEMO_COVER_DIR}/{filename}"
    return ""


class Command(BaseCommand):
    help = "Create or update demo categories and recognizable games for GameVault."

    CATEGORIES = (
        ("Action", "action"),
        ("RPG", "rpg"),
        ("Adventure", "adventure"),
        ("Horror", "horror"),
        ("Indie", "indie"),
        ("Strategy", "strategy"),
        ("Racing", "racing"),
        ("Simulation", "simulation"),
    )

    GAMES: tuple[dict[str, Any], ...] = (
        {
            "name": "Cyberpunk 2077",
            "slug": "cyberpunk-2077",
            "description": (
                "Неоновий рольовий бойовик про найманця у мегаполісі майбутнього, "
                "де імпланти, вибір і репутація змінюють кожне завдання."
            ),
            "price": Decimal("1599.00"),
            "category_slug": "rpg",
            "platform": Product.Platform.PC,
            "developer": "CD Projekt Red",
            "publisher": "CD Projekt",
            "release_date": date(2020, 12, 10),
            "stock": 36,
            "discount_percent": 20,
            "is_active": True,
            "is_featured": True,
            "cover": "cyberpunk-2077.svg",
        },
        {
            "name": "The Witcher 3: Wild Hunt",
            "slug": "the-witcher-3-wild-hunt",
            "description": (
                "Велика фентезійна RPG про мисливця на чудовиськ, політичні інтриги "
                "та подорожі відкритим світом із сильними сюжетними виборами."
            ),
            "price": Decimal("899.00"),
            "category_slug": "rpg",
            "platform": Product.Platform.PC,
            "developer": "CD Projekt Red",
            "publisher": "CD Projekt",
            "release_date": date(2015, 5, 19),
            "stock": 44,
            "discount_percent": 35,
            "is_active": True,
            "is_featured": True,
            "cover": "the-witcher-3-wild-hunt.svg",
        },
        {
            "name": "Red Dead Redemption 2",
            "slug": "red-dead-redemption-2",
            "description": (
                "Кінематографічна пригода про банду на згасаючому Дикому Заході, "
                "де спокійні поїздки, перестрілки й моральні рішення мають вагу."
            ),
            "price": Decimal("1499.00"),
            "category_slug": "adventure",
            "platform": Product.Platform.PLAYSTATION,
            "developer": "Rockstar Games",
            "publisher": "Rockstar Games",
            "release_date": date(2018, 10, 26),
            "stock": 28,
            "discount_percent": 15,
            "is_active": True,
            "is_featured": True,
            "cover": "red-dead-redemption-2.svg",
        },
        {
            "name": "Grand Theft Auto V Enhanced",
            "slug": "grand-theft-auto-v-enhanced",
            "description": (
                "Сатиричний кримінальний екшн у великому місті з трьома героями, "
                "пограбуваннями, погонями й відкритим світом для експериментів."
            ),
            "price": Decimal("1199.00"),
            "category_slug": "action",
            "platform": Product.Platform.XBOX,
            "developer": "Rockstar North",
            "publisher": "Rockstar Games",
            "release_date": date(2022, 3, 15),
            "stock": 31,
            "discount_percent": 10,
            "is_active": True,
            "is_featured": False,
            "cover": "grand-theft-auto-v-enhanced.svg",
        },
        {
            "name": "Elden Ring",
            "slug": "elden-ring",
            "description": (
                "Темне фентезі з відкритим світом, складними босами та свободою "
                "будувати героя під власний стиль бою й дослідження."
            ),
            "price": Decimal("1799.00"),
            "category_slug": "rpg",
            "platform": Product.Platform.PLAYSTATION,
            "developer": "FromSoftware",
            "publisher": "Bandai Namco Entertainment",
            "release_date": date(2022, 2, 25),
            "stock": 22,
            "discount_percent": 0,
            "is_active": True,
            "is_featured": True,
            "cover": "elden-ring.svg",
        },
        {
            "name": "Baldur's Gate 3",
            "slug": "baldurs-gate-3",
            "description": (
                "Партійна RPG з тактичними боями, живими діалогами та рішеннями, "
                "які помітно змінюють пригоди загону."
            ),
            "price": Decimal("1999.00"),
            "category_slug": "rpg",
            "platform": Product.Platform.PC,
            "developer": "Larian Studios",
            "publisher": "Larian Studios",
            "release_date": date(2023, 8, 3),
            "stock": 18,
            "discount_percent": 0,
            "is_active": True,
            "is_featured": True,
            "cover": "baldurs-gate-3.svg",
        },
        {
            "name": "Resident Evil Village",
            "slug": "resident-evil-village",
            "description": (
                "Напружений горор у засніженому селищі з дослідженням, ресурсним "
                "менеджментом і небезпечними зустрічами за кожними дверима."
            ),
            "price": Decimal("1099.00"),
            "category_slug": "horror",
            "platform": Product.Platform.PLAYSTATION,
            "developer": "Capcom",
            "publisher": "Capcom",
            "release_date": date(2021, 5, 7),
            "stock": 16,
            "discount_percent": 25,
            "is_active": True,
            "is_featured": False,
            "cover": "resident-evil-village.svg",
        },
        {
            "name": "DOOM Eternal",
            "slug": "doom-eternal",
            "description": (
                "Швидкий шутер із агресивним ритмом, важким саундтреком і аренами, "
                "де постійний рух важливіший за укриття."
            ),
            "price": Decimal("999.00"),
            "category_slug": "action",
            "platform": Product.Platform.XBOX,
            "developer": "id Software",
            "publisher": "Bethesda Softworks",
            "release_date": date(2020, 3, 20),
            "stock": 24,
            "discount_percent": 30,
            "is_active": True,
            "is_featured": False,
            "cover": "doom-eternal.svg",
        },
        {
            "name": "Hades",
            "slug": "hades",
            "description": (
                "Динамічний roguelike про втечу з підземного світу, де кожна спроба "
                "відкриває нові здібності, жарти й сімейні конфлікти богів."
            ),
            "price": Decimal("699.00"),
            "category_slug": "indie",
            "platform": Product.Platform.NINTENDO_SWITCH,
            "developer": "Supergiant Games",
            "publisher": "Supergiant Games",
            "release_date": date(2020, 9, 17),
            "stock": 38,
            "discount_percent": 15,
            "is_active": True,
            "is_featured": True,
            "cover": "hades.svg",
        },
        {
            "name": "Hollow Knight",
            "slug": "hollow-knight",
            "description": (
                "Атмосферна метроїдванія про підземне королівство з точними боями, "
                "таємними проходами й меланхолійною казковою подачею."
            ),
            "price": Decimal("449.00"),
            "category_slug": "indie",
            "platform": Product.Platform.NINTENDO_SWITCH,
            "developer": "Team Cherry",
            "publisher": "Team Cherry",
            "release_date": date(2017, 2, 24),
            "stock": 42,
            "discount_percent": 0,
            "is_active": True,
            "is_featured": False,
            "cover": "hollow-knight.svg",
        },
        {
            "name": "Stardew Valley",
            "slug": "stardew-valley",
            "description": (
                "Затишна фермерська симуляція про врожай, ремесло, дружбу з містянами "
                "та повільне облаштування власного куточка."
            ),
            "price": Decimal("399.00"),
            "category_slug": "simulation",
            "platform": Product.Platform.PC,
            "developer": "ConcernedApe",
            "publisher": "ConcernedApe",
            "release_date": date(2016, 2, 26),
            "stock": 55,
            "discount_percent": 0,
            "is_active": True,
            "is_featured": False,
            "cover": "stardew-valley.svg",
        },
        {
            "name": "Forza Horizon 5",
            "slug": "forza-horizon-5",
            "description": (
                "Яскраві перегони відкритим світом із фестивальною атмосферою, "
                "великим автопарком і трасами від пустелі до тропічних доріг."
            ),
            "price": Decimal("1699.00"),
            "category_slug": "racing",
            "platform": Product.Platform.XBOX,
            "developer": "Playground Games",
            "publisher": "Xbox Game Studios",
            "release_date": date(2021, 11, 9),
            "stock": 21,
            "discount_percent": 10,
            "is_active": True,
            "is_featured": False,
            "cover": "forza-horizon-5.svg",
        },
        {
            "name": "Sid Meier's Civilization VI",
            "slug": "sid-meiers-civilization-vi",
            "description": (
                "Покрокова стратегія про розвиток цивілізації від перших міст до "
                "космічних амбіцій, дипломатії та культурного суперництва."
            ),
            "price": Decimal("799.00"),
            "category_slug": "strategy",
            "platform": Product.Platform.PC,
            "developer": "Firaxis Games",
            "publisher": "2K",
            "release_date": date(2016, 10, 21),
            "stock": 33,
            "discount_percent": 40,
            "is_active": True,
            "is_featured": False,
            "cover": "sid-meiers-civilization-vi.svg",
        },
        {
            "name": "Frostpunk",
            "slug": "frostpunk",
            "description": (
                "Сувора стратегія виживання про місто серед льодової катастрофи, "
                "де кожен закон і виробниче рішення має людську ціну."
            ),
            "price": Decimal("649.00"),
            "category_slug": "strategy",
            "platform": Product.Platform.PC,
            "developer": "11 bit studios",
            "publisher": "11 bit studios",
            "release_date": date(2018, 4, 24),
            "stock": 27,
            "discount_percent": 20,
            "is_active": True,
            "is_featured": False,
            "cover": "frostpunk.svg",
        },
        {
            "name": "Disco Elysium",
            "slug": "disco-elysium",
            "description": (
                "Детективна RPG без звичних боїв, зате з гострими діалогами, "
                "психологічними перевірками й містом, яке пам'ятає кожну поразку."
            ),
            "price": Decimal("749.00"),
            "category_slug": "adventure",
            "platform": Product.Platform.PC,
            "developer": "ZA/UM",
            "publisher": "ZA/UM",
            "release_date": date(2019, 10, 15),
            "stock": 19,
            "discount_percent": 30,
            "is_active": True,
            "is_featured": False,
            "cover": "disco-elysium.svg",
        },
        {
            "name": "Terraria",
            "slug": "terraria",
            "description": (
                "Пісочниця про копання, будівництво й битви з босами, де маленький "
                "піксельний світ швидко перетворюється на особисту пригоду."
            ),
            "price": Decimal("299.00"),
            "category_slug": "adventure",
            "platform": Product.Platform.PC,
            "developer": "Re-Logic",
            "publisher": "Re-Logic",
            "release_date": date(2011, 5, 16),
            "stock": 60,
            "discount_percent": 0,
            "is_active": True,
            "is_featured": False,
            "cover": "terraria.svg",
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
            cover = data.pop("cover")
            data["category"] = categories[category_slug]
            data["image"] = demo_cover_path(cover)
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
