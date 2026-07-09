"""Create or update a realistic demo catalog for local development."""

from datetime import date
from decimal import Decimal
from pathlib import Path
from shutil import copy2
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import ProtectedError

from products.models import Category, Product

STATIC_COVER_DIR = Path("static/images/demo/covers")
MEDIA_COVER_DIR = Path("products/demo/covers")
COVER_EXTENSIONS = (".webp", ".jpg", ".jpeg", ".png")

LEGACY_DEMO_PRODUCT_SLUGS = {
    "neon-drift",
    "mythic-realms",
    "stellar-frontier",
    "iron-protocol",
    "kingdoms-of-aether",
    "echoes-in-the-dark",
    "velocity-apex",
    "pixelbound",
    "ashen-crown",
    "tactical-horizon",
    "night-signal",
    "circuit-legends",
}


class Command(BaseCommand):
    help = "Create or update realistic demo categories and games for GameVault."

    CATEGORIES = (
        ("Action", "action"),
        ("RPG", "rpg"),
        ("Adventure", "adventure"),
        ("Horror", "horror"),
        ("Indie", "indie"),
        ("Strategy", "strategy"),
        ("Racing", "racing"),
        ("Simulation", "simulation"),
        ("Open World", "open-world"),
        ("Shooter", "shooter"),
    )

    GAMES: tuple[dict[str, Any], ...] = (
        {
            "name": "Cyberpunk 2077",
            "slug": "cyberpunk-2077",
            "description": (
                "Неоновий рольовий бойовик про найманця у мегаполісі майбутнього, "
                "де імпланти, репутація й вибір впливають на кожне завдання."
            ),
            "price": Decimal("1599.00"),
            "category_slug": "open-world",
            "platform": Product.Platform.PC,
            "developer": "CD Projekt Red",
            "publisher": "CD Projekt",
            "release_date": date(2020, 12, 10),
            "stock": 36,
            "discount_percent": 20,
            "is_featured": True,
        },
        {
            "name": "The Witcher 3: Wild Hunt",
            "slug": "the-witcher-3-wild-hunt",
            "description": (
                "Велика фентезійна RPG про мисливця на чудовиськ, сильні сюжетні "
                "вибори та подорожі світом, повним небезпечних контрактів."
            ),
            "price": Decimal("899.00"),
            "category_slug": "rpg",
            "platform": Product.Platform.PC,
            "developer": "CD Projekt Red",
            "publisher": "CD Projekt",
            "release_date": date(2015, 5, 19),
            "stock": 44,
            "discount_percent": 35,
            "is_featured": True,
        },
        {
            "name": "Red Dead Redemption 2",
            "slug": "red-dead-redemption-2",
            "description": (
                "Кінематографічна пригода про банду на згасаючому Дикому Заході, "
                "де спокійні поїздки й важкі рішення мають однакову вагу."
            ),
            "price": Decimal("1499.00"),
            "category_slug": "open-world",
            "platform": Product.Platform.PLAYSTATION,
            "developer": "Rockstar Games",
            "publisher": "Rockstar Games",
            "release_date": date(2018, 10, 26),
            "stock": 28,
            "discount_percent": 15,
            "is_featured": True,
        },
        {
            "name": "Grand Theft Auto V Enhanced",
            "slug": "grand-theft-auto-v-enhanced",
            "description": (
                "Сатиричний кримінальний екшн із трьома героями, пограбуваннями, "
                "погонями й великим містом для вільних експериментів."
            ),
            "price": Decimal("1199.00"),
            "category_slug": "open-world",
            "platform": Product.Platform.XBOX,
            "developer": "Rockstar North",
            "publisher": "Rockstar Games",
            "release_date": date(2022, 3, 15),
            "stock": 31,
            "discount_percent": 10,
            "is_featured": False,
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
            "is_featured": True,
        },
        {
            "name": "Baldur's Gate 3",
            "slug": "baldurs-gate-3",
            "description": (
                "Партійна RPG з тактичними боями, живими діалогами та рішеннями, "
                "які помітно змінюють шлях загону."
            ),
            "price": Decimal("1999.00"),
            "category_slug": "rpg",
            "platform": Product.Platform.PC,
            "developer": "Larian Studios",
            "publisher": "Larian Studios",
            "release_date": date(2023, 8, 3),
            "stock": 18,
            "discount_percent": 0,
            "is_featured": True,
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
            "is_featured": False,
        },
        {
            "name": "DOOM Eternal",
            "slug": "doom-eternal",
            "description": (
                "Швидкий шутер із агресивним ритмом, важким саундтреком і аренами, "
                "де постійний рух важливіший за укриття."
            ),
            "price": Decimal("999.00"),
            "category_slug": "shooter",
            "platform": Product.Platform.XBOX,
            "developer": "id Software",
            "publisher": "Bethesda Softworks",
            "release_date": date(2020, 3, 20),
            "stock": 24,
            "discount_percent": 30,
            "is_featured": False,
        },
        {
            "name": "Hades",
            "slug": "hades",
            "description": (
                "Динамічний roguelike про втечу з підземного світу, де кожна "
                "спроба відкриває нові здібності й діалоги з богами."
            ),
            "price": Decimal("699.00"),
            "category_slug": "indie",
            "platform": Product.Platform.NINTENDO_SWITCH,
            "developer": "Supergiant Games",
            "publisher": "Supergiant Games",
            "release_date": date(2020, 9, 17),
            "stock": 38,
            "discount_percent": 15,
            "is_featured": True,
        },
        {
            "name": "Hollow Knight",
            "slug": "hollow-knight",
            "description": (
                "Атмосферна метроїдванія про підземне королівство з точними боями, "
                "таємними проходами й меланхолійною подачею."
            ),
            "price": Decimal("449.00"),
            "category_slug": "indie",
            "platform": Product.Platform.NINTENDO_SWITCH,
            "developer": "Team Cherry",
            "publisher": "Team Cherry",
            "release_date": date(2017, 2, 24),
            "stock": 42,
            "discount_percent": 0,
            "is_featured": False,
        },
        {
            "name": "Stardew Valley",
            "slug": "stardew-valley",
            "description": (
                "Затишна фермерська симуляція про врожай, ремесло, дружбу з "
                "містянами і повільне облаштування власного куточка."
            ),
            "price": Decimal("399.00"),
            "category_slug": "simulation",
            "platform": Product.Platform.PC,
            "developer": "ConcernedApe",
            "publisher": "ConcernedApe",
            "release_date": date(2016, 2, 26),
            "stock": 55,
            "discount_percent": 0,
            "is_featured": False,
        },
        {
            "name": "Forza Horizon 5",
            "slug": "forza-horizon-5",
            "description": (
                "Яскраві перегони відкритим світом із фестивальною атмосферою, "
                "великим автопарком і трасами від пустелі до тропіків."
            ),
            "price": Decimal("1699.00"),
            "category_slug": "racing",
            "platform": Product.Platform.XBOX,
            "developer": "Playground Games",
            "publisher": "Xbox Game Studios",
            "release_date": date(2021, 11, 9),
            "stock": 21,
            "discount_percent": 10,
            "is_featured": False,
        },
        {
            "name": "Sid Meier's Civilization VI",
            "slug": "sid-meiers-civilization-vi",
            "description": (
                "Покрокова стратегія про розвиток цивілізації від перших міст "
                "до космічних амбіцій, дипломатії й культурного суперництва."
            ),
            "price": Decimal("799.00"),
            "category_slug": "strategy",
            "platform": Product.Platform.PC,
            "developer": "Firaxis Games",
            "publisher": "2K",
            "release_date": date(2016, 10, 21),
            "stock": 33,
            "discount_percent": 40,
            "is_featured": False,
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
            "is_featured": False,
        },
        {
            "name": "Disco Elysium",
            "slug": "disco-elysium",
            "description": (
                "Детективна RPG без звичних боїв, зате з гострими діалогами, "
                "психологічними перевірками й містом, яке пам'ятає поразки."
            ),
            "price": Decimal("749.00"),
            "category_slug": "adventure",
            "platform": Product.Platform.PC,
            "developer": "ZA/UM",
            "publisher": "ZA/UM",
            "release_date": date(2019, 10, 15),
            "stock": 19,
            "discount_percent": 30,
            "is_featured": False,
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
            "is_featured": False,
        },
        {
            "name": "Dying Light",
            "slug": "dying-light",
            "description": (
                "Паркур-екшн про виживання у зараженому місті, де денні вилазки "
                "швидко змінюються небезпечними нічними переслідуваннями."
            ),
            "price": Decimal("699.00"),
            "category_slug": "horror",
            "platform": Product.Platform.PC,
            "developer": "Techland",
            "publisher": "Techland Publishing",
            "release_date": date(2015, 1, 27),
            "stock": 26,
            "discount_percent": 25,
            "is_featured": False,
        },
        {
            "name": "Mortal Kombat 11",
            "slug": "mortal-kombat-11",
            "description": (
                "Видовищний файтинг із різкими дуелями, знайомими героями, "
                "кінематографічною кампанією та великою кількістю прийомів."
            ),
            "price": Decimal("899.00"),
            "category_slug": "action",
            "platform": Product.Platform.PLAYSTATION,
            "developer": "NetherRealm Studios",
            "publisher": "Warner Bros. Games",
            "release_date": date(2019, 4, 23),
            "stock": 29,
            "discount_percent": 35,
            "is_featured": False,
        },
        {
            "name": "No Man's Sky",
            "slug": "no-mans-sky",
            "description": (
                "Космічна пригода про дослідження планет, кораблі, бази й відкриття "
                "невідомих систем у процедурно створеному всесвіті."
            ),
            "price": Decimal("1299.00"),
            "category_slug": "open-world",
            "platform": Product.Platform.PC,
            "developer": "Hello Games",
            "publisher": "Hello Games",
            "release_date": date(2016, 8, 12),
            "stock": 34,
            "discount_percent": 20,
            "is_featured": False,
        },
        {
            "name": "Kingdom Come: Deliverance",
            "slug": "kingdom-come-deliverance",
            "description": (
                "Історична RPG у Богемії XV століття з приземленим боєм, побутовими "
                "деталями та довгим шляхом від селянина до воїна."
            ),
            "price": Decimal("799.00"),
            "category_slug": "rpg",
            "platform": Product.Platform.PC,
            "developer": "Warhorse Studios",
            "publisher": "Deep Silver",
            "release_date": date(2018, 2, 13),
            "stock": 23,
            "discount_percent": 30,
            "is_featured": False,
        },
    )

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete known demo products and recreate the demo catalog.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        if options["reset"]:
            self._reset_demo_catalog()

        categories: dict[str, Category] = {}
        for name, slug in self.CATEGORIES:
            category, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name},
            )
            categories[slug] = category

        created_count = 0
        updated_count = 0
        covers_found = 0
        for game in self.GAMES:
            data = game.copy()
            category_slug = data.pop("category_slug")
            slug = data.pop("slug")
            data["category"] = categories[category_slug]
            data["is_active"] = True
            data["image"] = self._prepare_cover(slug)
            if data["image"]:
                covers_found += 1
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
                f"{updated_count} games updated, "
                f"{covers_found} local covers linked."
            )
        )

    def _reset_demo_catalog(self) -> None:
        """Delete known seed-created products before recreating the catalog."""
        demo_slugs = {game["slug"] for game in self.GAMES}
        product_slugs = demo_slugs | LEGACY_DEMO_PRODUCT_SLUGS
        category_slugs = {slug for _, slug in self.CATEGORIES} | {
            "action",
            "rpg",
            "strategy",
            "horror",
            "racing",
            "indie",
        }
        try:
            deleted_products, _ = Product.objects.filter(
                slug__in=product_slugs,
            ).delete()
        except ProtectedError as exc:
            raise CommandError(
                "Cannot reset demo catalog because some demo products are "
                "linked to orders. Remove those orders first or run without "
                "--reset to update records in place."
            ) from exc

        deleted_categories, _ = Category.objects.filter(
            slug__in=category_slugs,
            products__isnull=True,
        ).delete()
        self.stdout.write(
            "Reset demo catalog: "
            f"{deleted_products} product rows and "
            f"{deleted_categories} empty category rows removed."
        )

    def _prepare_cover(self, slug: str) -> str:
        """Copy a user-provided static cover into MEDIA for ImageField usage."""
        source = self._find_static_cover(slug)
        if source is None:
            return ""

        target_dir = Path(settings.MEDIA_ROOT) / MEDIA_COVER_DIR
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / source.name
        copy2(source, target)
        return str(MEDIA_COVER_DIR / source.name).replace("\\", "/")

    def _find_static_cover(self, slug: str) -> Path | None:
        static_cover_dir = Path(settings.BASE_DIR) / STATIC_COVER_DIR
        for extension in COVER_EXTENSIONS:
            candidate = static_cover_dir / f"{slug}{extension}"
            if candidate.exists():
                return candidate
        return None
