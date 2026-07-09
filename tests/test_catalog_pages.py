from decimal import Decimal
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product
from reviews.models import Review


class CatalogPagesTests(TestCase):
    action: Category
    rpg: Category
    active_product: Product
    second_product: Product
    inactive_product: Product
    related_product: Product
    user: Any
    review: Review

    @classmethod
    def setUpTestData(cls) -> None:
        cls.action = Category.objects.create(name="Action", slug="action")
        cls.rpg = Category.objects.create(name="RPG", slug="rpg")
        cls.active_product = cls.create_product(
            name="Alpha Quest",
            slug="alpha-quest",
            category=cls.action,
            platform=Product.Platform.PC,
            price=Decimal("50.00"),
        )
        cls.second_product = cls.create_product(
            name="Beta Kingdom",
            slug="beta-kingdom",
            category=cls.rpg,
            platform=Product.Platform.XBOX,
            price=Decimal("100.00"),
        )
        cls.inactive_product = cls.create_product(
            name="Hidden Game",
            slug="hidden-game",
            category=cls.action,
            platform=Product.Platform.PLAYSTATION,
            price=Decimal("75.00"),
            is_active=False,
        )

        related_products = []
        for number in range(10):
            related_products.append(
                cls.create_product(
                    name=f"Extra Game {number}",
                    slug=f"extra-game-{number}",
                    category=cls.action,
                    platform=Product.Platform.PC,
                    price=Decimal("200.00") + number,
                )
            )
        cls.related_product = related_products[0]

        user_model = get_user_model()
        cls.user = user_model.objects.create_user(
            username="reviewer",
            password="test-password",
        )
        cls.review = Review.objects.create(
            product=cls.active_product,
            user=cls.user,
            rating=5,
            comment="Чудова гра для тесту каталогу.",
        )

    @classmethod
    def create_product(
        cls,
        *,
        name: str,
        slug: str,
        category: Category,
        platform: str,
        price: Decimal,
        is_active: bool = True,
    ) -> Product:
        return Product.objects.create(
            name=name,
            slug=slug,
            description=f"Description for {name}",
            price=price,
            category=category,
            platform=platform,
            developer="Test Studio",
            publisher="Test Publisher",
            stock=10,
            is_active=is_active,
        )

    def test_product_list_uses_public_catalog_url(self) -> None:
        self.assertEqual(reverse("products:product_list"), "/products/")

    def test_product_list_returns_200(self) -> None:
        response = self.client.get(reverse("products:product_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "products/product_list.html")

    def test_product_list_shows_only_active_products(self) -> None:
        response = self.client.get(reverse("products:product_list"))
        products = list(response.context["products"])

        self.assertTrue(all(product.is_active for product in products))
        self.assertNotIn(self.inactive_product, products)

    def test_search_by_name(self) -> None:
        response = self.client.get(
            reverse("products:product_list"),
            {"q": "Alpha"},
        )

        self.assertContains(response, self.active_product.name)
        self.assertNotContains(response, self.second_product.name)

    def test_filter_by_category(self) -> None:
        response = self.client.get(
            reverse("products:product_list"),
            {"category": self.rpg.slug},
        )

        self.assertContains(response, self.second_product.name)
        self.assertNotContains(response, self.active_product.name)

    def test_filter_by_platform(self) -> None:
        response = self.client.get(
            reverse("products:product_list"),
            {"platform": Product.Platform.XBOX},
        )

        self.assertContains(response, self.second_product.name)
        self.assertNotContains(response, self.active_product.name)

    def test_filter_by_price_range(self) -> None:
        response = self.client.get(
            reverse("products:product_list"),
            {"min_price": "60", "max_price": "110"},
        )

        self.assertContains(response, self.second_product.name)
        self.assertNotContains(response, self.active_product.name)
        self.assertNotContains(response, self.related_product.name)

    def test_sort_by_price_ascending(self) -> None:
        response = self.client.get(
            reverse("products:product_list"),
            {"sort": "price_asc"},
        )
        products = list(response.context["products"])

        self.assertEqual(products[0], self.active_product)
        self.assertEqual(products[1], self.second_product)

    def test_product_list_is_paginated(self) -> None:
        response = self.client.get(
            reverse("products:product_list"),
            {"page": 2},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page_obj"].number, 2)
        self.assertEqual(len(response.context["products"]), 3)

    def test_product_detail_returns_200(self) -> None:
        response = self.client.get(self.active_product.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "products/product_detail.html")
        self.assertContains(response, self.active_product.name)

    def test_product_detail_uses_fallback_when_cover_is_missing(self) -> None:
        response = self.client.get(self.active_product.get_absolute_url())

        self.assertContains(response, "detail-placeholder")
        self.assertContains(response, self.active_product.name)

    def test_inactive_product_detail_returns_404(self) -> None:
        response = self.client.get(self.inactive_product.get_absolute_url())

        self.assertEqual(response.status_code, 404)

    def test_product_detail_displays_reviews(self) -> None:
        response = self.client.get(self.active_product.get_absolute_url())

        self.assertContains(response, self.review.comment)
        self.assertContains(response, self.user.username)

    def test_product_detail_displays_related_products(self) -> None:
        response = self.client.get(self.active_product.get_absolute_url())
        related_products = list(response.context["related_products"])

        self.assertNotIn(self.active_product, related_products)
        self.assertTrue(
            all(product.category == self.action for product in related_products)
        )
        self.assertContains(response, related_products[0].name)
        self.assertLessEqual(len(related_products), 4)

    def test_product_detail_can_be_rendered_in_english(self) -> None:
        response = self.client.get(
            self.active_product.get_absolute_url(),
            HTTP_ACCEPT_LANGUAGE="en",
        )

        self.assertContains(response, "Developer")
        self.assertContains(response, "Price")
        self.assertContains(response, "Add to cart")
        self.assertContains(response, "Reviews: 1")


class SeedDemoGamesCommandTests(TestCase):
    def test_command_creates_expected_real_games_and_categories(self) -> None:
        call_command("seed_demo_games", verbosity=0)

        expected_product_slugs = {
            "cyberpunk-2077",
            "the-witcher-3-wild-hunt",
            "elden-ring",
            "baldurs-gate-3",
        }
        expected_category_slugs = {"rpg", "action", "horror", "strategy"}

        self.assertTrue(
            expected_product_slugs.issubset(
                set(Product.objects.values_list("slug", flat=True))
            )
        )
        self.assertTrue(
            expected_category_slugs.issubset(
                set(Category.objects.values_list("slug", flat=True))
            )
        )

    def test_product_list_shows_seeded_real_game(self) -> None:
        call_command("seed_demo_games", verbosity=0)

        response = self.client.get(
            reverse("products:product_list"),
            {"q": "Cyberpunk"},
        )

        self.assertContains(response, "Cyberpunk 2077")
        self.assertNotContains(response, "Neon Drift")

    def test_command_is_idempotent(self) -> None:
        call_command("seed_demo_games", verbosity=0)
        category_count = Category.objects.count()
        product_count = Product.objects.count()

        call_command("seed_demo_games", verbosity=0)

        self.assertEqual(Category.objects.count(), category_count)
        self.assertEqual(Product.objects.count(), product_count)
        self.assertGreaterEqual(product_count, 20)

    def test_reset_recreates_demo_catalog(self) -> None:
        category = Category.objects.create(name="Old Action", slug="old-action")
        Product.objects.create(
            name="Neon Drift",
            slug="neon-drift",
            description="Old demo product.",
            price=Decimal("10.00"),
            category=category,
            platform=Product.Platform.PC,
            stock=5,
            is_active=True,
        )

        call_command("seed_demo_games", "--reset", verbosity=0)

        self.assertFalse(Product.objects.filter(slug="neon-drift").exists())
        self.assertEqual(Product.objects.filter(slug="cyberpunk-2077").count(), 1)
        self.assertEqual(Product.objects.count(), 20)
