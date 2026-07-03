from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from orders.cart import CART_SESSION_KEY
from orders.models import Order, OrderItem
from products.models import Category, Product


class CheckoutFlowTests(TestCase):
    category: Category
    product: Product

    @classmethod
    def setUpTestData(cls) -> None:
        cls.category = Category.objects.create(name="Action", slug="action")
        cls.product = Product.objects.create(
            name="Checkout Test",
            slug="checkout-test",
            description="Checkout test product",
            price=Decimal("100.00"),
            category=cls.category,
            platform=Product.Platform.PC,
            stock=5,
            discount_percent=10,
            is_active=True,
        )

    def checkout_data(self) -> dict[str, str]:
        return {
            "full_name": "Олена Коваль",
            "email": "olena@example.com",
            "phone": "+380501234567",
            "city": "Київ",
            "address": "вул. Хрещатик, 1",
            "payment_method": Order.PaymentMethod.CARD,
        }

    def add_to_cart(self, quantity: int = 2) -> None:
        self.client.post(
            reverse("cart:add", args=[self.product.pk]),
            {"quantity": quantity},
        )

    def test_checkout_redirects_empty_cart(self) -> None:
        response = self.client.get(reverse("checkout:form"), follow=True)

        self.assertRedirects(response, reverse("cart:detail"))
        self.assertContains(response, "Ваш кошик порожній")

    def test_checkout_page_opens_with_cart_items(self) -> None:
        self.add_to_cart()

        response = self.client.get(reverse("checkout:form"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orders/checkout.html")
        self.assertContains(response, self.product.name)
        self.assertContains(response, "₴180")

    def test_valid_checkout_creates_order_and_order_item(self) -> None:
        self.add_to_cart()

        response = self.client.post(
            reverse("checkout:form"),
            self.checkout_data(),
        )

        order = Order.objects.get()
        order_item = OrderItem.objects.get()
        self.assertRedirects(
            response,
            reverse("checkout:success", args=[order.pk]),
        )
        self.assertIsNone(order.user)
        self.assertEqual(order.first_name, "Олена")
        self.assertEqual(order.last_name, "Коваль")
        self.assertEqual(order.total_price, Decimal("180.00"))
        self.assertEqual(order_item.order, order)
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price, Decimal("90.00"))

    def test_authenticated_checkout_links_order_to_user(self) -> None:
        user = get_user_model().objects.create_user(
            username="checkout-player",
            password="StrongPassword123!",
        )
        self.client.force_login(user)
        self.add_to_cart()

        self.client.post(reverse("checkout:form"), self.checkout_data())

        self.assertEqual(Order.objects.get().user, user)

    def test_valid_checkout_decreases_stock(self) -> None:
        self.add_to_cart(quantity=3)

        self.client.post(reverse("checkout:form"), self.checkout_data())

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)

    def test_valid_checkout_clears_session_cart(self) -> None:
        self.add_to_cart()

        self.client.post(reverse("checkout:form"), self.checkout_data())

        self.assertNotIn(CART_SESSION_KEY, self.client.session)

    def test_checkout_rejects_quantity_above_latest_stock(self) -> None:
        self.add_to_cart(quantity=3)
        Product.objects.filter(pk=self.product.pk).update(stock=2)

        response = self.client.post(
            reverse("checkout:form"),
            self.checkout_data(),
        )

        self.assertRedirects(response, reverse("cart:detail"))
        self.assertFalse(Order.objects.exists())
        self.assertEqual(
            self.client.session[CART_SESSION_KEY][str(self.product.pk)][
                "quantity"
            ],
            3,
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)

    def test_success_page_renders_order_number_and_total(self) -> None:
        self.add_to_cart()
        self.client.post(reverse("checkout:form"), self.checkout_data())
        order = Order.objects.get()

        response = self.client.get(
            reverse("checkout:success", args=[order.pk]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orders/checkout_success.html")
        self.assertContains(response, f"Замовлення №{order.pk}")
        self.assertContains(response, "₴180")

    def test_success_page_is_limited_to_checkout_session(self) -> None:
        self.add_to_cart()
        self.client.post(reverse("checkout:form"), self.checkout_data())
        order = Order.objects.get()

        response = Client().get(
            reverse("checkout:success", args=[order.pk]),
        )

        self.assertEqual(response.status_code, 404)

    def test_checkout_uses_ukrainian_by_default(self) -> None:
        self.add_to_cart()

        response = self.client.get(reverse("checkout:form"))

        self.assertContains(response, '<html lang="uk">')
        self.assertContains(response, "Оформлення замовлення")
        self.assertContains(response, "Повне ім’я")
        self.assertContains(response, "Підтвердити замовлення")

    def test_checkout_can_be_rendered_in_english(self) -> None:
        self.add_to_cart()

        response = self.client.get(
            reverse("checkout:form"),
            HTTP_ACCEPT_LANGUAGE="en",
        )

        self.assertContains(response, '<html lang="en">')
        self.assertContains(response, "Checkout")
        self.assertContains(response, "Full name")
        self.assertContains(response, "Confirm order")
