from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from products.models import Product


class HomePageTests(TestCase):
    def test_home_page_uses_expected_template(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/home.html")
        self.assertContains(response, "GameVault")

    def test_popular_genre_links_point_to_catalog_filters(self) -> None:
        call_command("seed_demo_games", "--reset", verbosity=0)

        response = self.client.get("/")
        content = response.content.decode()
        genre_section = content.split('class="genre-grid"', 1)[1].split(
            "</section>",
            1,
        )[0]

        self.assertNotIn('href="#"', genre_section)
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
                "elden-ring",
            )
        )

        response = self.client.get("/")

        for product in hero_products:
            self.assertContains(response, product.get_absolute_url())
            self.assertContains(response, product.cover_url)

    def test_home_platform_links_point_to_catalog_filters(self) -> None:
        response = self.client.get("/")

        self.assertContains(response, "Платформи")
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
