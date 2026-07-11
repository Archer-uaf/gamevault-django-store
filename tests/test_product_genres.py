from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from products.models import Category, Product


EXPECTED_GAME_GENRES = {
    'kingdom-come-deliverance': {'open-world', 'rpg'},
    'cyberpunk-2077': {'action', 'open-world', 'rpg'},
    'the-witcher-3-wild-hunt': {'action', 'open-world', 'rpg'},
    'dying-light': {'action', 'horror', 'open-world'},
    'forza-horizon-5': {'racing'},
    'hearts-of-iron-iv': {'strategy'},
    'no-mans-sky': {'adventure'},
    'terraria': {'adventure'},
    'disco-elysium': {'rpg'},
    'frostpunk': {'strategy'},
    'sid-meiers-civilization-vi': {'strategy'},
    'stardew-valley': {'simulation'},
    'hollow-knight': {'indie'},
    'hades': {'indie'},
    'doom-eternal': {'shooter'},
    'resident-evil-village': {'action', 'horror'},
    'baldurs-gate-3': {'rpg'},
    'elden-ring': {'action', 'rpg'},
    'grand-theft-auto-v-enhanced': {'action', 'open-world'},
    'red-dead-redemption-2': {'action', 'open-world'},
}


class ProductGenreTests(TestCase):
    action: Category
    rpg: Category
    product: Product

    @classmethod
    def setUpTestData(cls) -> None:
        cls.action = Category.objects.create(name="Action", slug="genre-action")
        cls.rpg = Category.objects.create(name="RPG", slug="genre-rpg")
        cls.product = Product.objects.create(
            name="Multi Genre Game",
            slug="multi-genre-game",
            description="A game with several genres.",
            price=Decimal("100.00"),
            category=cls.action,
            platform=Product.Platform.PC,
            stock=10,
        )
        cls.product.genres.set((cls.action, cls.rpg))

    def test_product_can_have_multiple_genres(self) -> None:
        self.assertEqual(
            set(self.product.genres.values_list("slug", flat=True)),
            {"genre-action", "genre-rpg"},
        )

    def test_web_catalog_filters_by_secondary_genre(self) -> None:
        response = self.client.get(
            reverse("products:product_list"),
            {"category": self.rpg.slug},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_product_detail_displays_all_genres(self) -> None:
        response = self.client.get(self.product.get_absolute_url())

        self.assertContains(response, self.action.name)
        self.assertContains(response, self.rpg.name)

    def test_api_filters_by_secondary_genre(self) -> None:
        client = APIClient()
        response = client.get(
            reverse("api:product-list"),
            {"category": self.rpg.slug},
        )

        self.assertEqual(response.status_code, 200)
        product_ids = {item["id"] for item in response.json()["results"]}
        self.assertIn(self.product.pk, product_ids)

    def test_api_product_contains_all_genres(self) -> None:
        client = APIClient()
        response = client.get(
            reverse("api:product-detail", args=[self.product.pk]),
        )

        self.assertEqual(response.status_code, 200)
        genre_slugs = {item["slug"] for item in response.json()["genres"]}
        self.assertEqual(genre_slugs, {"genre-action", "genre-rpg"})


class DemoCatalogGenreTests(TestCase):
    def test_seed_command_assigns_exact_catalog_genres(self) -> None:
        call_command("seed_demo_games", reset=True, verbosity=0)

        for slug, expected_genres in EXPECTED_GAME_GENRES.items():
            with self.subTest(slug=slug):
                product = Product.objects.get(slug=slug)
                actual_genres = set(
                    product.genres.values_list("slug", flat=True)
                )
                self.assertEqual(actual_genres, expected_genres)
