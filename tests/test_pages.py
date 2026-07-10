from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils.formats import localize

from products.models import Product


class HomePageTests(TestCase):
    def test_home_page_uses_expected_template(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/home.html")
        self.assertContains(response, "GameVault")

    def test_base_loads_google_fonts_once(self) -> None:
        response = self.client.get("/")
        content = response.content.decode()

        self.assertEqual(content.count("fonts.googleapis.com/css2"), 1)
        self.assertEqual(content.count("fonts.gstatic.com"), 1)
        self.assertEqual(content.count("family=Exo+2"), 1)
        self.assertEqual(content.count("family=Manrope"), 1)

    def test_popular_genre_links_point_to_catalog_filters(self) -> None:
        call_command("seed_demo_games", "--reset", verbosity=0)

        response = self.client.get("/")
        content = response.content.decode()
        genre_section = content.split('class="genre-grid"', 1)[1].split(
            "</section>",
            1,
        )[0]

        self.assertNotIn('href="#"', genre_section)
        self.assertNotIn("Перейти до добірки", genre_section)
        self.assertIn(
            'class="genre-card__arrow" aria-hidden="true"',
            genre_section,
        )
        for slug in (
            "action",
            "rpg",
            "adventure",
            "horror",
            "strategy",
            "racing",
            "indie",
            "simulation",
            "open-world",
            "shooter",
        ):
            self.assertContains(
                response,
                f'{reverse("products:product_list")}?category={slug}',
            )

    def test_home_recommended_games_use_real_product_cards(self) -> None:
        call_command("seed_demo_games", "--reset", verbosity=0)
        product = Product.objects.get(slug="cyberpunk-2077")

        response = self.client.get("/")
        content = response.content.decode()

        self.assertContains(response, product.name)
        self.assertContains(response, product.get_absolute_url())
        self.assertContains(response, product.cover_url)
        self.assertEqual(content.count('class="game-card game-card--interactive"'), 3)
        self.assertNotContains(response, "Каталог ще порожній")
        self.assertNotContains(response, "Рекомендовані ігри з'являться")

    def test_home_hero_uses_real_product_cover_links(self) -> None:
        call_command("seed_demo_games", "--reset", verbosity=0)
        hero_products = Product.objects.filter(
            slug__in=(
                "cyberpunk-2077",
                "the-witcher-3-wild-hunt",
                "hearts-of-iron-iv",
            )
        )

        response = self.client.get("/")
        content = response.content.decode()
        hero_section = content.split('class="hero-hot-deals"', 1)[1].split(
            "</section>",
            1,
        )[0]

        for product in hero_products:
            self.assertContains(response, product.get_absolute_url())
            self.assertContains(response, product.cover_url)
            self.assertIn(f"₴{localize(product.price)}", hero_section)
            self.assertIn(f"₴{localize(product.final_price)}", hero_section)

        self.assertEqual(
            hero_section.count('class="hero-hot-card hero-hot-card--'),
            3,
        )
        self.assertEqual(hero_section.count("Детальніше"), 3)

    def test_home_hero_uses_dynamic_featured_product_description(self) -> None:
        call_command("seed_demo_games", "--reset", verbosity=0)
        product = Product.objects.get(slug="cyberpunk-2077")
        product.description = (
            "<strong>Динамічний опис featured-гри</strong> показує актуальний "
            "текст продукту без прив'язки до конкретної назви та без HTML-розмітки."
        )
        product.save(update_fields=["description"])

        response = self.client.get("/")
        content = response.content.decode()
        hero_section = content.split('class="hero-hot-deals"', 1)[1].split(
            "</section>",
            1,
        )[0]

        self.assertIn("Динамічний опис featured-гри", hero_section)
        self.assertNotIn("<strong>Динамічний опис featured-гри</strong>", hero_section)
        self.assertNotIn("Футуристична Action-RPG", hero_section)

    def test_home_recommended_prices_distinguish_discounted_products(self) -> None:
        call_command("seed_demo_games", "--reset", verbosity=0)
        discounted_product = Product.objects.get(slug="cyberpunk-2077")
        regular_product = Product.objects.get(slug="hearts-of-iron-iv")
        regular_product.discount_percent = 0
        regular_product.save(update_fields=["discount_percent"])

        response = self.client.get("/")
        content = response.content.decode()
        featured_section = content.split('id="featured-games"', 1)[1].split(
            "</section>",
            1,
        )[0]
        discounted_card = featured_section.split(
            f'href="{discounted_product.get_absolute_url()}"',
            1,
        )[1].split("</a>", 1)[0]
        regular_card = featured_section.split(
            f'href="{regular_product.get_absolute_url()}"',
            1,
        )[1].split("</a>", 1)[0]

        self.assertIn('<del class="old-price">', discounted_card)
        self.assertIn(f"₴{localize(discounted_product.price)}", discounted_card)
        self.assertIn(
            f"₴{localize(discounted_product.final_price)}",
            discounted_card,
        )
        self.assertIn(f"-{discounted_product.discount_percent}%", discounted_card)
        self.assertNotIn('<del class="old-price">', regular_card)
        self.assertIn(f"₴{localize(regular_product.price)}", regular_card)

    def test_home_platform_links_point_to_catalog_filters(self) -> None:
        response = self.client.get("/")
        content = response.content.decode()
        platform_section = content.split('class="platform-grid"', 1)[1].split(
            "</section>",
            1,
        )[0]

        self.assertContains(response, "Платформи")
        self.assertNotIn("Дивитися ігри", platform_section)
        self.assertIn(
            'class="platform-card__arrow" aria-hidden="true"',
            platform_section,
        )
        for platform in (
            Product.Platform.PC,
            Product.Platform.PLAYSTATION,
            Product.Platform.XBOX,
            Product.Platform.NINTENDO_SWITCH,
        ):
            self.assertContains(
                response,
                f'{reverse("products:product_list")}?platform={platform}',
            )
