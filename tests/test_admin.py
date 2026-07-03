from decimal import Decimal
from typing import Any

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from orders.models import Order
from products.models import Category, Product


class AdminManagementTests(TestCase):
    admin_user: Any
    category: Category
    product: Product

    @classmethod
    def setUpTestData(cls) -> None:
        user_model = get_user_model()
        cls.admin_user = user_model.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin-password",
        )
        cls.category = Category.objects.create(name="Action", slug="action")
        cls.product = Product.objects.create(
            name="Admin Analytics Game",
            slug="admin-analytics-game",
            description="Product used by admin tests.",
            price=Decimal("100.00"),
            category=cls.category,
            platform=Product.Platform.PC,
            stock=5,
            is_active=False,
        )

    def setUp(self) -> None:
        self.client.force_login(self.admin_user)

    @classmethod
    def create_order(
        cls,
        *,
        status: str,
        total_price: Decimal,
        email: str,
    ) -> Order:
        return Order.objects.create(
            status=status,
            total_price=total_price,
            first_name="Олена",
            last_name="Коваль",
            email=email,
            phone="+380501234567",
            city="Київ",
            shipping_address="вул. Хрещатик, 1",
            payment_method=Order.PaymentMethod.CARD,
        )

    def test_product_admin_action_marks_products_active(self) -> None:
        response = self.client.post(
            reverse("admin:products_product_changelist"),
            {
                "action": "mark_active",
                "_selected_action": [self.product.pk],
            },
        )

        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertTrue(self.product.is_active)

    def test_product_admin_action_marks_products_inactive(self) -> None:
        self.product.is_active = True
        self.product.save(update_fields=("is_active",))

        response = self.client.post(
            reverse("admin:products_product_changelist"),
            {
                "action": "mark_inactive",
                "_selected_action": [self.product.pk],
            },
        )

        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertFalse(self.product.is_active)

    def test_order_admin_action_changes_only_allowed_status(self) -> None:
        pending_order = self.create_order(
            status=Order.Status.PENDING,
            total_price=Decimal("50.00"),
            email="pending@example.com",
        )
        cancelled_order = self.create_order(
            status=Order.Status.CANCELLED,
            total_price=Decimal("75.00"),
            email="cancelled@example.com",
        )

        response = self.client.post(
            reverse("admin:orders_order_changelist"),
            {
                "action": "mark_as_paid",
                "_selected_action": [pending_order.pk, cancelled_order.pk],
            },
        )

        self.assertEqual(response.status_code, 302)
        pending_order.refresh_from_db()
        cancelled_order.refresh_from_db()
        self.assertEqual(pending_order.status, Order.Status.PAID)
        self.assertEqual(cancelled_order.status, Order.Status.CANCELLED)

    def test_order_admin_changelist_displays_analytics(self) -> None:
        self.create_order(
            status=Order.Status.PENDING,
            total_price=Decimal("50.00"),
            email="pending@example.com",
        )
        self.create_order(
            status=Order.Status.PAID,
            total_price=Decimal("100.00"),
            email="paid@example.com",
        )

        response = self.client.get(reverse("admin:orders_order_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Усього замовлень")
        summary = response.context["order_summary"]
        self.assertEqual(summary["total_orders"], 2)
        self.assertEqual(summary["total_revenue"], Decimal("100.00"))
        self.assertEqual(summary["pending_orders"], 1)
        self.assertEqual(summary["paid_orders"], 1)

    def test_product_admin_search_and_filter_return_200(self) -> None:
        response = self.client.get(
            reverse("admin:products_product_changelist"),
            {
                "q": "Analytics",
                "category__id__exact": str(self.category.pk),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)

    def test_order_admin_analytics_can_be_rendered_in_english(self) -> None:
        response = self.client.get(
            reverse("admin:orders_order_changelist"),
            HTTP_ACCEPT_LANGUAGE="en",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total orders")
        self.assertContains(response, "Revenue")
