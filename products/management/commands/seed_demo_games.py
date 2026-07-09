"""Create or reset realistic demo catalog data for local development."""

from datetime import date
from decimal import Decimal
from typing import Any

from django.core.management.base import BaseCommand

from orders.models import Order
from products.models import Category, Product


def text(*parts: str) -> str:
    """Join short text fragments into one readable sentence."""
    return " ".join(parts)


def steam_header(app_id: int) -> str:
    """Return a public Steam header image URL used only for demo covers."""
    return f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"


class Command(BaseCommand):
    help = "Create or reset realistic demo categories and games for GameVault."

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
            "description": text(
                "Відкрита RPG про найманця у Найт-Сіті, де стиль,",
                "імпланти та вибір визначають шлях крізь небезпечне майбутнє.",
            ),
            "description_en": text(
                "An open-world RPG about a mercenary in Night City, where style,",
                "implants, and hard choices shape a dangerous future.",
            ),
            "price": Decimal("1299.00"),
            "category_slug": "rpg",
            "platform": Product.Platform.PC,
            "developer": "CD PROJEKT RED",
            "publisher": "CD PROJEKT RED",
            "release_date": date(2020, 12, 10),
            "stock": 42,
            "discount_percent": 25,
            "is_featured": True,
            "cover_url": steam_header(1091500),
        },
        {
            "name": "The Witcher 3: Wild Hunt",
            "slug": "the-witcher-3-wild-hunt",
            "description": text(
                "Темне фентезі про Геральта з Рівії, полювання на чудовиськ",
                "і рішення, які залишають слід у великих та малих історіях.",
            ),
            "description_en": text(
                "A dark fantasy journey with Geralt of Rivia, monster contracts,",
                "and choices that echo through grand and personal stories.",
            ),
            "price": Decimal("899.00"),
            "category_slug": "rpg",
            "platform": Product.Platform.PC,
            "developer": "CD PROJEKT RED",
            "publisher": "CD PROJEKT RED",
            "release_date": date(2015, 5, 18),
            "stock": 38,
            "discount_percent": 40,
            "is_featured": True,
            "cover_url": steam_header(292030),
        },
        {
            "name": "Red Dead Redemption 2",
            "slug": "red-dead-redemption-2",
            "description": text(
                "Кінематографічна історія банди на заході епохи Дикого Заходу",
                "з повільним темпом, великим світом і сильними персонажами.",
            ),
            "description_en": text(
                "A cinematic outlaw story set at the end of the Wild West,",
                "built around a vast world, deliberate pacing,",
                "and memorable characters.",
            ),
            "price": Decimal("1599.00"),
            "category_slug": "open-world",
            "platform": Product.Platform.PLAYSTATION,
            "developer": "Rockstar Games",
            "publisher": "Rockstar Games",
            "release_date": date(2019, 12, 5),
            "stock": 27,
            "discount_percent": 30,
            "is_featured": True,
            "cover_url": steam_header(1174180),
        },
        {
            "name": "Grand Theft Auto V Enhanced",
            "slug": "grand-theft-auto-v-enhanced",
            "description": text(
                "Кримінальна пісочниця про Лос-Сантос із трьома героями,",
                "швидкими погонями та великою кількістю хаотичних можливостей.",
            ),
            "description_en": text(
                "A Los Santos crime sandbox with three protagonists, fast chases,",
                "and a huge set of chaotic open-world possibilities.",
            ),
            "price": Decimal("1199.00"),
            "category_slug": "action",
            "platform": Product.Platform.XBOX,
            "developer": "Rockstar North",
            "publisher": "Rockstar Games",
            "release_date": date(2015, 4, 14),
            "stock": 33,
            "discount_percent": 20,
            "is_featured": False,
            "cover_url": steam_header(271590),
        },
        {
            "name": "Elden Ring",
            "slug": "elden-ring",
            "description": text(
                "Велика action RPG про мандрівку Міжзем'ям, складні битви",
                "з босами та дослідження руїн, фортець і прихованих шляхів.",
            ),
            "description_en": text(
                "A vast action RPG across the Lands Between, with demanding boss",
                "fights and exploration through ruins, castles, and hidden paths.",
            ),
            "price": Decimal("1799.00"),
            "category_slug": "rpg",
            "platform": Product.Platform.PC,
            "developer": "FromSoftware",
            "publisher": "Bandai Namco Entertainment",
            "release_date": date(2022, 2, 25),
            "stock": 31,
            "discount_percent": 15,
            "is_featured": True,
            "cover_url": steam_header(1245620),
        },
        {
            "name": "Baldur's Gate 3",
            "slug": "baldurs-gate-3",
            "description": text(
                "Партійна RPG у світі Dungeons & Dragons з тактичними боями,",
                "свободою вибору та діалогами, що справді змінюють подорож.",
            ),
            "description_en": text(
                "A party-based Dungeons & Dragons RPG with tactical combat,",
                "rich choices, and conversations that meaningfully change the journey.",
            ),
            "price": Decimal("1699.00"),
            "category_slug": "rpg",
            "platform": Product.Platform.PC,
            "developer": "Larian Studios",
            "publisher": "Larian Studios",
            "release_date": date(2023, 8, 3),
            "stock": 24,
            "discount_percent": 0,
            "is_featured": True,
            "cover_url": steam_header(1086940),
        },
        {
            "name": "Resident Evil Village",
            "slug": "resident-evil-village",
            "description": text(
                "Напружений survival horror у засніженому селі з моторошними",
                "локаціями, обмеженими ресурсами та небезпечними зустрічами.",
            ),
            "description_en": text(
                "A tense survival horror game set around a snow-covered village,",
                "with eerie locations, scarce resources, and dangerous encounters.",
            ),
            "price": Decimal("1099.00"),
            "category_slug": "horror",
            "platform": Product.Platform.PLAYSTATION,
            "developer": "Capcom",
            "publisher": "Capcom",
            "release_date": date(2021, 5, 7),
            "stock": 18,
            "discount_percent": 35,
            "is_featured": False,
            "cover_url": steam_header(1196590),
        },
        {
            "name": "DOOM Eternal",
            "slug": "doom-eternal",
            "description": text(
                "Швидкий shooter про агресивні арени, точний рух",
                "і безперервний натиск демонів, де кожна помилка коштує дорого.",
            ),
            "description_en": text(
                "A fast shooter built around aggressive arenas, precise movement,",
                "and relentless demon pressure where every mistake matters.",
            ),
            "price": Decimal("999.00"),
            "category_slug": "shooter",
            "platform": Product.Platform.PC,
            "developer": "id Software",
            "publisher": "Bethesda Softworks",
            "release_date": date(2020, 3, 20),
            "stock": 29,
            "discount_percent": 45,
            "is_featured": False,
            "cover_url": steam_header(782330),
        },
        {
            "name": "Hades",
            "slug": "hades",
            "description": text(
                "Динамічний roguelike про втечу з підземного світу, де кожна",
                "спроба відкриває нові діалоги, зброю та комбінації здібностей.",
            ),
            "description_en": text(
                "A dynamic roguelike escape from the underworld, where every run",
                "unlocks new conversations, weapons, and ability combinations.",
            ),
            "price": Decimal("599.00"),
            "category_slug": "indie",
            "platform": Product.Platform.NINTENDO_SWITCH,
            "developer": "Supergiant Games",
            "publisher": "Supergiant Games",
            "release_date": date(2020, 9, 17),
            "stock": 36,
            "discount_percent": 20,
            "is_featured": True,
            "cover_url": steam_header(1145360),
        },
        {
            "name": "Hollow Knight",
            "slug": "hollow-knight",
            "description": text(
                "Атмосферна metroidvania про підземне королівство, точні бої,",
                "тихе дослідження та секрети, заховані за кожним поворотом.",
            ),
            "description_en": text(
                "An atmospheric metroidvania through an underground kingdom,",
                "with precise combat, quiet exploration,",
                "and secrets around every turn.",
            ),
            "price": Decimal("449.00"),
            "category_slug": "indie",
            "platform": Product.Platform.NINTENDO_SWITCH,
            "developer": "Team Cherry",
            "publisher": "Team Cherry",
            "release_date": date(2017, 2, 24),
            "stock": 40,
            "discount_percent": 10,
            "is_featured": False,
            "cover_url": steam_header(367520),
        },
        {
            "name": "Stardew Valley",
            "slug": "stardew-valley",
            "description": text(
                "Затишна фермерська simulation про сезонні врожаї, дружбу",
                "з мешканцями містечка, риболовлю та спокійний розвиток садиби.",
            ),
            "description_en": text(
                "A cozy farming simulation about seasonal crops, town friendships,",
                "fishing, and slowly building a peaceful homestead.",
            ),
            "price": Decimal("399.00"),
            "category_slug": "simulation",
            "platform": Product.Platform.NINTENDO_SWITCH,
            "developer": "ConcernedApe",
            "publisher": "ConcernedApe",
            "release_date": date(2016, 2, 26),
            "stock": 50,
            "discount_percent": 0,
            "is_featured": False,
            "cover_url": steam_header(413150),
        },
        {
            "name": "Forza Horizon 5",
            "slug": "forza-horizon-5",
            "description": text(
                "Яскраві перегони відкритим світом Мексики з сотнями авто,",
                "фестивальними подіями та маршрутами для різних стилів водіння.",
            ),
            "description_en": text(
                "Bright open-world racing across Mexico, with hundreds of cars,",
                "festival events, and routes for different driving styles.",
            ),
            "price": Decimal("1499.00"),
            "category_slug": "racing",
            "platform": Product.Platform.XBOX,
            "developer": "Playground Games",
            "publisher": "Xbox Game Studios",
            "release_date": date(2021, 11, 9),
            "stock": 26,
            "discount_percent": 25,
            "is_featured": True,
            "cover_url": steam_header(1551360),
        },
        {
            "name": "Sid Meier's Civilization VI",
            "slug": "sid-meiers-civilization-vi",
            "description": text(
                "Покрокова strategy про розвиток цивілізації від перших",
                "поселень до космічних амбіцій, дипломатії та наукових проривів.",
            ),
            "description_en": text(
                "A turn-based strategy game about guiding a civilization from",
                "early settlements to space ambitions, diplomacy, and progress.",
            ),
            "price": Decimal("799.00"),
            "category_slug": "strategy",
            "platform": Product.Platform.PC,
            "developer": "Firaxis Games",
            "publisher": "2K",
            "release_date": date(2016, 10, 21),
            "stock": 34,
            "discount_percent": 50,
            "is_featured": False,
            "cover_url": steam_header(289070),
        },
        {
            "name": "Frostpunk",
            "slug": "frostpunk",
            "description": text(
                "Морозна strategy про місто на межі виживання, де кожен закон,",
                "ресурс і моральний компроміс впливають на долю людей.",
            ),
            "description_en": text(
                "A frozen survival strategy game where every law, resource,",
                "and moral compromise shapes the fate of a city on the edge.",
            ),
            "price": Decimal("699.00"),
            "category_slug": "strategy",
            "platform": Product.Platform.PC,
            "developer": "11 bit studios",
            "publisher": "11 bit studios",
            "release_date": date(2018, 4, 24),
            "stock": 21,
            "discount_percent": 35,
            "is_featured": False,
            "cover_url": steam_header(323190),
        },
        {
            "name": "Disco Elysium",
            "slug": "disco-elysium",
            "description": text(
                "Незвична RPG-детектив про розслідування, внутрішні голоси героя",
                "та місто, яке розкривається через розмови й наслідки вибору.",
            ),
            "description_en": text(
                "An unusual detective RPG about an investigation, inner voices,",
                "and a city revealed through conversations and consequences.",
            ),
            "price": Decimal("749.00"),
            "category_slug": "rpg",
            "platform": Product.Platform.PC,
            "developer": "ZA/UM",
            "publisher": "ZA/UM",
            "release_date": date(2019, 10, 15),
            "stock": 19,
            "discount_percent": 30,
            "is_featured": False,
            "cover_url": steam_header(632470),
        },
        {
            "name": "Terraria",
            "slug": "terraria",
            "description": text(
                "Піксельна sandbox-пригода про копання, будівництво, босів",
                "і відкриття небезпечніших шарів випадково створеного світу.",
            ),
            "description_en": text(
                "A pixel sandbox adventure about digging, building, bosses,",
                "and uncovering more dangerous layers of a generated world.",
            ),
            "price": Decimal("299.00"),
            "category_slug": "adventure",
            "platform": Product.Platform.PC,
            "developer": "Re-Logic",
            "publisher": "Re-Logic",
            "release_date": date(2011, 5, 16),
            "stock": 55,
            "discount_percent": 0,
            "is_featured": False,
            "cover_url": steam_header(105600),
        },
        {
            "name": "Dying Light",
            "slug": "dying-light",
            "description": text(
                "Survival action у зараженому місті, де денний паркур",
                "змінюється нічною втечею від значно небезпечніших ворогів.",
            ),
            "description_en": text(
                "A survival action game in an infected city, where daytime parkour",
                "turns into night escapes from far more dangerous enemies.",
            ),
            "price": Decimal("799.00"),
            "category_slug": "horror",
            "platform": Product.Platform.PLAYSTATION,
            "developer": "Techland",
            "publisher": "Techland",
            "release_date": date(2015, 1, 27),
            "stock": 22,
            "discount_percent": 45,
            "is_featured": False,
            "cover_url": steam_header(239140),
        },
        {
            "name": "Mortal Kombat 11",
            "slug": "mortal-kombat-11",
            "description": text(
                "Брутальний файтинг з упізнаваними бійцями, точними комбінаціями",
                "та видовищними поєдинками для локальної й онлайн-гри.",
            ),
            "description_en": text(
                "A brutal fighting game with recognizable characters, precise combos,",
                "and dramatic matches for local and online play.",
            ),
            "price": Decimal("899.00"),
            "category_slug": "action",
            "platform": Product.Platform.PLAYSTATION,
            "developer": "NetherRealm Studios",
            "publisher": "Warner Bros. Games",
            "release_date": date(2019, 4, 23),
            "stock": 28,
            "discount_percent": 35,
            "is_featured": False,
            "cover_url": steam_header(976310),
        },
        {
            "name": "No Man's Sky",
            "slug": "no-mans-sky",
            "description": text(
                "Космічна adventure про процедурні планети, бази, кораблі",
                "та спокійне або ризиковане дослідження нескінченного всесвіту.",
            ),
            "description_en": text(
                "A space adventure about procedural planets, bases, ships,",
                "and calm or risky exploration across an endless universe.",
            ),
            "price": Decimal("1199.00"),
            "category_slug": "adventure",
            "platform": Product.Platform.PC,
            "developer": "Hello Games",
            "publisher": "Hello Games",
            "release_date": date(2016, 8, 12),
            "stock": 30,
            "discount_percent": 20,
            "is_featured": False,
            "cover_url": steam_header(275850),
        },
        {
            "name": "Kingdom Come: Deliverance",
            "slug": "kingdom-come-deliverance",
            "description": text(
                "Історична RPG у середньовічній Богемії з приземленими боями,",
                "побутовими деталями та шляхом від селянина до воїна.",
            ),
            "description_en": text(
                "A historical RPG in medieval Bohemia, with grounded combat,",
                "everyday detail, and a path from village life to hard-earned skill.",
            ),
            "price": Decimal("849.00"),
            "category_slug": "rpg",
            "platform": Product.Platform.PC,
            "developer": "Warhorse Studios",
            "publisher": "Warhorse Studios",
            "release_date": date(2018, 2, 13),
            "stock": 23,
            "discount_percent": 40,
            "is_featured": False,
            "cover_url": steam_header(379430),
        },
    )

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete previous demo products and recreate the real game catalog.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        if options["reset"]:
            self._reset_demo_catalog()

        categories = self._upsert_categories()
        created_count = 0
        updated_count = 0

        for game in self.GAMES:
            data = game.copy()
            category_slug = data.pop("category_slug")
            slug = data.pop("slug")
            data["category"] = categories[category_slug]
            data["is_active"] = True
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

    def _upsert_categories(self) -> dict[str, Category]:
        categories: dict[str, Category] = {}
        for name, slug in self.CATEGORIES:
            category, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name},
            )
            categories[slug] = category
        return categories

    def _reset_demo_catalog(self) -> None:
        demo_slugs = self._demo_slugs()
        orders = Order.objects.filter(items__product__slug__in=demo_slugs).distinct()
        deleted_orders = orders.count()
        orders.delete()

        products = Product.objects.filter(slug__in=demo_slugs)
        deleted_products = products.count()
        products.delete()

        category_slugs = {slug for _, slug in self.CATEGORIES}
        Category.objects.filter(slug__in=category_slugs, products__isnull=True).delete()

        self.stdout.write(
            "Demo catalog reset: "
            f"{deleted_orders} orders deleted, "
            f"{deleted_products} demo products deleted."
        )

    @classmethod
    def _demo_slugs(cls) -> set[str]:
        product_slugs = {game["slug"] for game in cls.GAMES}
        return product_slugs | cls.LEGACY_DEMO_PRODUCT_SLUGS
