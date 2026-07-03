from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from products.models import Category, Product


class CartAPITests(TestCase):
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()
        self.category = Category.objects.create(
            name="API Cart",
            slug="api-cart",
        )
        self.product = Product.objects.create(
            name="API Cart Game",
            slug="api-cart-game",
            description="A game added to the API cart.",
            price=Decimal("100.00"),
            discount_percent=20,
            category=self.category,
            platform=Product.Platform.PC,
            stock=5,
        )
        self.inactive_product = Product.objects.create(
            name="Inactive API Cart Game",
            slug="inactive-api-cart-game",
            description="A hidden game.",
            price=Decimal("50.00"),
            category=self.category,
            platform=Product.Platform.PC,
            stock=5,
            is_active=False,
        )

    def test_empty_cart_returns_empty_payload(self) -> None:
        response = self.client.get(reverse("api:cart"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "items": [],
            "total": "0.00",
            "total_items": 0,
        })

    def test_add_product_to_cart(self) -> None:
        response = self.client.post(
            reverse("api:cart-item-add"),
            {"product_id": self.product.pk, "quantity": 2},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertEqual(payload["total_items"], 2)
        self.assertEqual(payload["total"], "160.00")
        self.assertEqual(payload["items"][0]["product"]["id"], self.product.pk)
        self.assertEqual(payload["items"][0]["quantity"], 2)
        self.assertEqual(payload["items"][0]["unit_price"], "80.00")
        self.assertEqual(payload["items"][0]["line_total"], "160.00")

    def test_add_same_product_increases_quantity(self) -> None:
        self.client.post(
            reverse("api:cart-item-add"),
            {"product_id": self.product.pk, "quantity": 1},
            format="json",
        )

        response = self.client.post(
            reverse("api:cart-item-add"),
            {"product_id": self.product.pk, "quantity": 2},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["items"][0]["quantity"], 3)
        self.assertEqual(response.json()["total_items"], 3)

    def test_cannot_add_inactive_product(self) -> None:
        response = self.client.post(
            reverse("api:cart-item-add"),
            {"product_id": self.inactive_product.pk, "quantity": 1},
            format="json",
        )

        self.assertEqual(response.status_code, 404)

    def test_cannot_add_more_than_stock(self) -> None:
        response = self.client.post(
            reverse("api:cart-item-add"),
            {"product_id": self.product.pk, "quantity": 6},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        cart_response = self.client.get(reverse("api:cart"))
        self.assertEqual(cart_response.json()["total_items"], 0)

    def test_patch_item_quantity(self) -> None:
        self.client.post(
            reverse("api:cart-item-add"),
            {"product_id": self.product.pk, "quantity": 1},
            format="json",
        )

        response = self.client.patch(
            reverse("api:cart-item-detail", args=[self.product.pk]),
            {"quantity": 4},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items"][0]["quantity"], 4)
        self.assertEqual(response.json()["total"], "320.00")

    def test_patch_item_above_stock_is_rejected(self) -> None:
        self.client.post(
            reverse("api:cart-item-add"),
            {"product_id": self.product.pk, "quantity": 1},
            format="json",
        )

        response = self.client.patch(
            reverse("api:cart-item-detail", args=[self.product.pk]),
            {"quantity": 6},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        cart_response = self.client.get(reverse("api:cart"))
        self.assertEqual(cart_response.json()["items"][0]["quantity"], 1)

    def test_delete_item(self) -> None:
        self.client.post(
            reverse("api:cart-item-add"),
            {"product_id": self.product.pk, "quantity": 2},
            format="json",
        )

        response = self.client.delete(
            reverse("api:cart-item-detail", args=[self.product.pk]),
        )

        self.assertEqual(response.status_code, 204)
        cart_response = self.client.get(reverse("api:cart"))
        self.assertEqual(cart_response.json()["items"], [])
        self.assertEqual(cart_response.json()["total_items"], 0)

    def test_clear_cart(self) -> None:
        self.client.post(
            reverse("api:cart-item-add"),
            {"product_id": self.product.pk, "quantity": 2},
            format="json",
        )

        response = self.client.delete(reverse("api:cart"))

        self.assertEqual(response.status_code, 204)
        cart_response = self.client.get(reverse("api:cart"))
        self.assertEqual(cart_response.json()["items"], [])
        self.assertEqual(cart_response.json()["total"], "0.00")

    def test_schema_contains_cart_paths(self) -> None:
        response = self.client.get(reverse("schema"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/api/cart/")
        self.assertContains(response, "/api/cart/items/")
