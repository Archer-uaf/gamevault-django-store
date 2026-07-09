from decimal import Decimal
from typing import Any

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from orders.models import Order, OrderItem
from products.models import Category, Product
from reviews.models import Review


class CatalogAPITests(TestCase):
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()
        self.action = Category.objects.create(name="Action", slug="api-action")
        self.rpg = Category.objects.create(name="RPG", slug="api-rpg")
        self.first_product = self.create_product(
            name="Alpha API Game",
            slug="alpha-api-game",
            category=self.action,
            price=Decimal("50.00"),
        )
        self.second_product = self.create_product(
            name="Beta API Game",
            slug="beta-api-game",
            category=self.rpg,
            price=Decimal("100.00"),
            description="Searchable kingdom adventure.",
        )
        self.inactive_product = self.create_product(
            name="Hidden API Game",
            slug="hidden-api-game",
            category=self.action,
            price=Decimal("75.00"),
            is_active=False,
        )

    def test_products_list_is_public_and_active_only(self) -> None:
        response = self.client.get(reverse("api:product-list"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        product_ids = {product["id"] for product in payload["results"]}
        self.assertIn(self.first_product.pk, product_ids)
        self.assertIn(self.second_product.pk, product_ids)
        self.assertNotIn(self.inactive_product.pk, product_ids)

    def test_product_detail_is_public(self) -> None:
        response = self.client.get(
            reverse("api:product-detail", args=[self.first_product.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["slug"], self.first_product.slug)

    def test_product_filters_search_and_sorting_work(self) -> None:
        category_response = self.client.get(
            reverse("api:product-list"),
            {"category": self.rpg.slug},
        )
        price_response = self.client.get(
            reverse("api:product-list"),
            {"price_min": "60", "price_max": "110"},
        )
        search_response = self.client.get(
            reverse("api:product-list"),
            {"search": "kingdom"},
        )
        ascending_response = self.client.get(
            reverse("api:product-list"),
            {"ordering": "price"},
        )
        descending_response = self.client.get(
            reverse("api:product-list"),
            {"ordering": "-price"},
        )
        created_response = self.client.get(
            reverse("api:product-list"),
            {"ordering": "created_at"},
        )

        self.assertEqual(
            category_response.json()["results"][0]["id"],
            self.second_product.pk,
        )
        self.assertEqual(
            price_response.json()["results"][0]["id"],
            self.second_product.pk,
        )
        self.assertEqual(
            search_response.json()["results"][0]["id"],
            self.second_product.pk,
        )
        self.assertEqual(
            ascending_response.json()["results"][0]["id"],
            self.first_product.pk,
        )
        self.assertEqual(
            descending_response.json()["results"][0]["id"],
            self.second_product.pk,
        )
        self.assertEqual(
            created_response.json()["results"][0]["id"],
            self.first_product.pk,
        )

    def test_product_popularity_sort_uses_review_count(self) -> None:
        first_user = get_user_model().objects.create_user(username="api-reviewer-1")
        second_user = get_user_model().objects.create_user(username="api-reviewer-2")
        Review.objects.create(
            product=self.first_product,
            user=first_user,
            rating=5,
            comment="First API review.",
        )
        Review.objects.create(
            product=self.first_product,
            user=second_user,
            rating=4,
            comment="Second API review.",
        )

        response = self.client.get(
            reverse("api:product-list"),
            {"ordering": "-popularity"},
        )

        self.assertEqual(
            response.json()["results"][0]["id"],
            self.first_product.pk,
        )

    def test_categories_list_is_public(self) -> None:
        response = self.client.get(reverse("api:category-list"))

        self.assertEqual(response.status_code, 200)
        category_ids = {item["id"] for item in response.json()["results"]}
        self.assertIn(self.action.pk, category_ids)
        self.assertIn(self.rpg.pk, category_ids)

    @staticmethod
    def create_product(
        *,
        name: str,
        slug: str,
        category: Category,
        price: Decimal,
        description: str = "API product description.",
        is_active: bool = True,
    ) -> Product:
        return Product.objects.create(
            name=name,
            slug=slug,
            description=description,
            price=price,
            category=category,
            platform=Product.Platform.PC,
            stock=10,
            is_active=is_active,
        )


class AuthAPITests(TestCase):
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username="api-user",
            email="api-user@example.com",
            password="StrongPassword123!",
        )

    def test_register_creates_user(self) -> None:
        response = self.client.post(
            reverse("api:register"),
            {
                "username": "new-api-user",
                "email": "new-api-user@example.com",
                "password": "AnotherStrongPassword123!",
                "password_confirm": "AnotherStrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            get_user_model().objects.filter(username="new-api-user").exists()
        )
        self.assertNotIn("password", response.json())

    def test_jwt_token_endpoint_returns_token_pair(self) -> None:
        response = self.client.post(
            reverse("api:token"),
            {"username": "api-user", "password": "StrongPassword123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_me_requires_authentication(self) -> None:
        response = self.client.get(reverse("api:me"))

        self.assertEqual(response.status_code, 401)

    def test_me_returns_current_user(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("api:me"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], self.user.username)
        self.assertEqual(response.json()["email"], self.user.email)


class OrderAPITests(TestCase):
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username="order-api-user")
        self.other_user = get_user_model().objects.create_user(
            username="other-order-api-user"
        )
        category = Category.objects.create(name="Orders", slug="api-orders")
        self.product = Product.objects.create(
            name="API Order Game",
            slug="api-order-game",
            description="A game ordered through the API.",
            price=Decimal("100.00"),
            discount_percent=10,
            category=category,
            platform=Product.Platform.PC,
            stock=5,
        )

    def test_orders_list_requires_authentication(self) -> None:
        response = self.client.get(reverse("api:order-list"))

        self.assertEqual(response.status_code, 401)

    def test_user_sees_only_own_orders(self) -> None:
        own_order = self.create_order(user=self.user)
        other_order = self.create_order(user=self.other_user)
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("api:order-list"))

        order_ids = {order["id"] for order in response.json()["results"]}
        self.assertIn(own_order.pk, order_ids)
        self.assertNotIn(other_order.pk, order_ids)

    def test_order_api_uses_digital_status_labels(self) -> None:
        order = self.create_order(user=self.user)
        order.status = Order.Status.SHIPPED
        order.save(update_fields=("status",))
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("api:order-detail", args=[order.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status_display"], "Ключ надіслано")

    def test_order_detail_is_owner_only(self) -> None:
        other_order = self.create_order(user=self.other_user)
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            reverse("api:order-detail", args=[other_order.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_valid_api_order_creates_order_and_item(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse("api:order-list"),
            self.order_payload(quantity=2),
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        order = Order.objects.get()
        item = OrderItem.objects.get()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total_price, Decimal("180.00"))
        self.assertEqual(item.product, self.product)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.price, Decimal("90.00"))

    def test_valid_api_order_decreases_stock(self) -> None:
        self.client.force_authenticate(user=self.user)

        self.client.post(
            reverse("api:order-list"),
            self.order_payload(quantity=3),
            format="json",
        )

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)

    def test_cannot_order_more_than_stock(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse("api:order-list"),
            self.order_payload(quantity=6),
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Order.objects.exists())
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)

    def order_payload(self, *, quantity: int) -> dict[str, Any]:
        return {
            "items": [{"product_id": self.product.pk, "quantity": quantity}],
            "full_name": "Олена Коваль",
            "email": "olena@example.com",
            "phone": "+380501234567",
            "city": "Київ",
            "address": "вул. Хрещатик, 1",
            "payment_method": Order.PaymentMethod.CARD,
        }

    @staticmethod
    def create_order(*, user: Any) -> Order:
        return Order.objects.create(
            user=user,
            total_price=Decimal("100.00"),
            first_name="API",
            last_name="User",
            email="api-order@example.com",
            phone="+380000000000",
            city="Kyiv",
            shipping_address="Test street, 1",
            payment_method=Order.PaymentMethod.CARD,
        )


class ReviewAPITests(TestCase):
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username="review-api-user")
        category = Category.objects.create(name="Reviews", slug="api-reviews")
        self.product = Product.objects.create(
            name="API Review Game",
            slug="api-review-game",
            description="A game reviewed through the API.",
            price=Decimal("60.00"),
            category=category,
            platform=Product.Platform.PC,
            stock=5,
        )

    def test_reviews_list_is_public(self) -> None:
        Review.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            comment="Public API review.",
        )

        response = self.client.get(
            reverse("api:review-list"),
            {"product": self.product.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"][0]["rating"], 5)

    def test_unauthenticated_review_create_is_denied(self) -> None:
        response = self.client.post(
            reverse("api:review-list"),
            self.review_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertFalse(Review.objects.exists())

    def test_authenticated_user_without_purchase_cannot_review(self) -> None:
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse("api:review-list"),
            self.review_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Review.objects.exists())

    def test_user_with_cancelled_order_cannot_create_review(self) -> None:
        self.create_purchase(status=Order.Status.CANCELLED)
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse("api:review-list"),
            self.review_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Review.objects.exists())

    def test_authenticated_buyer_can_create_review(self) -> None:
        self.create_purchase()
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse("api:review-list"),
            self.review_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        review = Review.objects.get()
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.product, self.product)
        self.assertEqual(review.rating, 5)

    def test_duplicate_review_is_blocked(self) -> None:
        self.create_purchase()
        Review.objects.create(
            user=self.user,
            product=self.product,
            rating=4,
            comment="Existing API review.",
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            reverse("api:review-list"),
            self.review_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Review.objects.count(), 1)

    def review_payload(self) -> dict[str, Any]:
        return {
            "product_id": self.product.pk,
            "rating": 5,
            "comment": "Verified API review.",
        }

    def create_purchase(
        self,
        *,
        status: str = Order.Status.PENDING,
    ) -> Order:
        order = Order.objects.create(
            user=self.user,
            status=status,
            total_price=self.product.price,
            first_name="Review",
            last_name="Buyer",
            email="review-buyer@example.com",
            phone="+380000000000",
            city="Kyiv",
            shipping_address="Test street, 1",
            payment_method=Order.PaymentMethod.CARD,
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            price=self.product.price,
        )
        return order


class OpenAPIEndpointTests(TestCase):
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()

    def test_schema_endpoint_works(self) -> None:
        response = self.client.get(reverse("schema"))

        self.assertEqual(response.status_code, 200)

    def test_swagger_endpoint_works(self) -> None:
        response = self.client.get(reverse("swagger-ui"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "swagger-ui")
