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
            description="Український опис Alpha Quest.",
            description_en="English description for Alpha Quest.",
            cover_url="https://example.com/alpha.jpg",
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
        description: str | None = None,
        description_en: str = "",
        cover_url: str = "",
        stock: int = 10,
        is_active: bool = True,
    ) -> Product:
        return Product.objects.create(
            name=name,
            slug=slug,
            description=description or f"Description for {name}",
            description_en=description_en,
            price=price,
            category=category,
            cover_url=cover_url,
            platform=platform,
            developer="Test Studio",
            publisher="Test Publisher",
            stock=stock,
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

    def test_product_detail_uses_localized_description(self) -> None:
        ukrainian_response = self.client.get(self.active_product.get_absolute_url())
        english_response = self.client.get(
            self.active_product.get_absolute_url(),
            HTTP_ACCEPT_LANGUAGE="en",
        )

        self.assertContains(ukrainian_response, "Український опис Alpha Quest.")
        self.assertContains(english_response, "English description for Alpha Quest.")
        self.assertNotContains(english_response, "Український опис Alpha Quest.")

    def test_product_list_renders_cover_url_when_image_missing(self) -> None:
        response = self.client.get(
            reverse("products:product_list"),
            {"q": "Alpha"},
        )

        self.assertContains(response, self.active_product.name)
        self.assertContains(response, self.active_product.cover_url)

    def test_product_list_shows_stock_status_without_exact_number(self) -> None:
        Product.objects.filter(pk=self.active_product.pk).update(stock=30)

        response = self.client.get(
            reverse("products:product_list"),
            {"q": "Alpha"},
        )

        self.assertContains(response, "В наявності")
        self.assertNotContains(response, "В наявності: 30")

    def test_product_list_shows_low_stock_status(self) -> None:
        Product.objects.filter(pk=self.active_product.pk).update(stock=10)

        response = self.client.get(
            reverse("products:product_list"),
            {"q": "Alpha"},
        )

        self.assertContains(response, "Закінчується")
        self.assertNotContains(response, "В наявності: 10")

    def test_product_list_shows_out_of_stock_status(self) -> None:
        Product.objects.filter(pk=self.active_product.pk).update(stock=0)

        response = self.client.get(
            reverse("products:product_list"),
            {"q": "Alpha"},
        )

        self.assertContains(response, "Немає в наявності")

    def test_product_detail_stock_status_can_be_rendered_in_english(self) -> None:
        Product.objects.filter(pk=self.active_product.pk).update(stock=10)

        response = self.client.get(
            self.active_product.get_absolute_url(),
            HTTP_ACCEPT_LANGUAGE="en",
        )

        self.assertContains(response, "Low stock")
        self.assertNotContains(response, "In stock: 10")

    def test_product_detail_renders_cover_url_when_image_missing(self) -> None:
        response = self.client.get(self.active_product.get_absolute_url())

        self.assertContains(response, self.active_product.cover_url)


class SeedDemoGamesCommandTests(TestCase):
    def test_reset_creates_real_games_and_removes_fake_titles(self) -> None:
        Category.objects.create(name="Action", slug="action")
        Product.objects.create(
            name="Circuit Legends",
            slug="circuit-legends",
            description="Legacy fake title.",
            price=Decimal("100.00"),
            category=Category.objects.get(slug="action"),
            platform=Product.Platform.PC,
            stock=1,
        )

        call_command("seed_demo_games", "--reset", verbosity=0)

        product_names = set(Product.objects.values_list("name", flat=True))
        self.assertIn("Cyberpunk 2077", product_names)
        self.assertIn("The Witcher 3: Wild Hunt", product_names)
        self.assertIn("Elden Ring", product_names)
        self.assertIn("Hearts of Iron IV", product_names)
        self.assertNotIn("Circuit Legends", product_names)
        self.assertNotIn("Night Signal", product_names)
        self.assertNotIn("Tactical Horizon", product_names)
        self.assertNotIn("Mortal Kombat 11", product_names)

    def test_real_demo_games_have_covers_and_english_descriptions(self) -> None:
        call_command("seed_demo_games", "--reset", verbosity=0)

        products = Product.objects.all()
        self.assertEqual(products.filter(cover_url="").count(), 0)
        self.assertEqual(products.filter(description_en="").count(), 0)
        self.assertTrue(
            products.filter(
                slug="cyberpunk-2077",
                cover_url__contains="1091500",
            ).exists()
        )

    def test_real_demo_games_use_static_steam_price_snapshot(self) -> None:
        call_command("seed_demo_games", "--reset", verbosity=0)

        cyberpunk = Product.objects.get(slug="cyberpunk-2077")
        hearts = Product.objects.get(slug="hearts-of-iron-iv")

        self.assertGreater(cyberpunk.price, Decimal("0.00"))
        self.assertEqual(cyberpunk.discount_percent, 70)
        self.assertEqual(hearts.price, Decimal("1349.00"))
        self.assertEqual(hearts.discount_percent, 80)
        self.assertIn("394360", hearts.cover_url)

    def test_product_pages_render_seeded_real_covers(self) -> None:
        call_command("seed_demo_games", "--reset", verbosity=0)
        product = Product.objects.get(slug="elden-ring")

        list_response = self.client.get(
            reverse("products:product_list"),
            {"q": "Elden"},
        )
        detail_response = self.client.get(product.get_absolute_url())

        self.assertContains(list_response, "Elden Ring")
        self.assertContains(list_response, product.cover_url)
        self.assertContains(detail_response, product.cover_url)

    def test_seeded_product_description_is_localized(self) -> None:
        call_command("seed_demo_games", "--reset", verbosity=0)
        product = Product.objects.get(slug="cyberpunk-2077")

        ukrainian_response = self.client.get(product.get_absolute_url())
        english_response = self.client.get(
            product.get_absolute_url(),
            HTTP_ACCEPT_LANGUAGE="en",
        )

        self.assertContains(ukrainian_response, "Відкрита RPG про найманця")
        self.assertContains(english_response, "An open-world RPG about a mercenary")
        self.assertNotContains(english_response, "Відкрита RPG про найманця")

    def test_command_is_idempotent_after_reset(self) -> None:
        call_command("seed_demo_games", "--reset", verbosity=0)
        category_count = Category.objects.count()
        product_count = Product.objects.count()

        call_command("seed_demo_games", verbosity=0)

        self.assertEqual(Category.objects.count(), category_count)
        self.assertEqual(Product.objects.count(), product_count)
        self.assertEqual(product_count, 20)
