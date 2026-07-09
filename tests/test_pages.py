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

    def test_home_popular_genre_links_point_to_catalog_filters(self) -> None:
        call_command("seed_demo_games", verbosity=0)

        response = self.client.get("/")

        for slug in ("action", "rpg", "horror", "strategy"):
            self.assertContains(
                response,
                f'{reverse("products:product_list")}?category={slug}',
            )

    def test_home_recommended_games_link_to_product_details(self) -> None:
        call_command("seed_demo_games", verbosity=0)

        response = self.client.get("/")
        product = Product.objects.get(slug="cyberpunk-2077")

        self.assertContains(response, product.name)
        self.assertContains(response, f'href="{product.get_absolute_url()}"')

    def test_home_recommended_games_use_cover_fallback(self) -> None:
        call_command("seed_demo_games", verbosity=0)

        response = self.client.get("/")

        self.assertContains(response, "game-placeholder")
        self.assertNotContains(response, 'href="#"')
