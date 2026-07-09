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
        call_command("seed_demo_games", "--reset", verbosity=0)

        response = self.client.get("/")

        for slug in ("action", "rpg", "horror", "strategy"):
            self.assertContains(
                response,
                f'{reverse("products:product_list")}?category={slug}',
            )
        self.assertNotContains(response, 'href="#"')

    def test_home_recommended_games_show_real_products_and_covers(self) -> None:
        call_command("seed_demo_games", "--reset", verbosity=0)
        product = Product.objects.get(slug="cyberpunk-2077")

        response = self.client.get("/")

        self.assertContains(response, "Cyberpunk 2077")
        self.assertContains(response, "The Witcher 3: Wild Hunt")
        self.assertContains(response, product.cover_url)
        self.assertContains(response, f'href="{product.get_absolute_url()}"')
        self.assertNotContains(response, "Каталог ще порожній")
