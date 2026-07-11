from decimal import Decimal
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase, override_settings
from django.shortcuts import resolve_url
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

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="checkout-player",
            email="checkout-player@example.com",
            password="StrongPassword123!",
        )

    def checkout_data(self) -> dict[str, str]:
        return {
            "email": "olena@example.com",
            "payment_method": Order.PaymentMethod.BANK_CARD_TEST,
        }

    def login_user(self) -> None:
        self.client.force_login(self.user)

    def add_to_cart(self, quantity: int = 2) -> None:
        self.client.post(
            reverse("cart:add", args=[self.product.pk]),
            {"quantity": quantity},
        )

    def test_anonymous_checkout_redirects_to_login_and_preserves_cart(self) -> None:
        self.add_to_cart()

        response = self.client.get(reverse("checkout:form"))

        self.assertEqual(response.status_code, 302)
        location = response.headers["Location"]
        self.assertTrue(location.startswith(resolve_url(settings.LOGIN_URL)))
        self.assertIn("next=", location)
        self.assertIn(CART_SESSION_KEY, self.client.session)

    @override_settings(ADMIN_EMAIL="")
    def test_valid_checkout_sends_customer_email_without_admin_email(self) -> None:
        self.login_user()
        self.add_to_cart()

        self.client.post(reverse("checkout:form"), self.checkout_data())

        order = Order.objects.get()
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertIn(str(order.pk), email.subject)
        self.assertEqual(email.to, [order.email])
        self.assertIn(str(order.total_price), email.body)
        self.assertIn("Ключ активації", email.body)
        self.assertIn("XXXXX-XXXXX-XXXXX", email.body)
        self.assertEqual(
            email.body.count("XXXXX-XXXXX-XXXXX"),
            2,
        )
        self.assertIn("Фізична доставка не потрібна", email.body)

    @override_settings(ADMIN_EMAIL="admin@example.com")
    def test_valid_checkout_sends_admin_notification(self) -> None:
        self.login_user()
        self.add_to_cart()

        response = self.client.post(
            reverse("checkout:form"),
            self.checkout_data(),
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 2)
        admin_email = next(
            email for email in mail.outbox if email.to == ["admin@example.com"]
        )
        order = Order.objects.get()
        self.assertIn(str(order.pk), admin_email.subject)
        self.assertIn(order.email, admin_email.body)

    @override_settings(ADMIN_EMAIL="")
    def test_checkout_succeeds_and_logs_when_email_delivery_fails(self) -> None:
        self.login_user()
        self.add_to_cart()

        with (
            patch(
                "orders.emails.send_mail",
                side_effect=RuntimeError("SMTP unavailable"),
            ) as send_mail_mock,
            patch("orders.emails.logger.exception") as log_exception_mock,
        ):
            response = self.client.post(
                reverse("checkout:form"),
                self.checkout_data(),
            )

        order = Order.objects.get()
        self.assertRedirects(
            response,
            reverse("checkout:success", args=[order.pk]),
        )
        self.assertEqual(OrderItem.objects.count(), 1)
        send_mail_mock.assert_called_once()
        log_exception_mock.assert_called_once_with(
            "Order email delivery failed.",
            extra={
                "order_id": order.pk,
                "notification_type": "customer_confirmation",
            },
        )

    def test_authenticated_checkout_redirects_empty_cart(self) -> None:
        self.login_user()

        response = self.client.get(reverse("checkout:form"), follow=True)

        self.assertRedirects(response, reverse("cart:detail"))
        self.assertContains(response, "Ваш кошик порожній")

    def test_checkout_page_only_shows_digital_fields(self) -> None:
        self.login_user()
        self.add_to_cart()

        response = self.client.get(reverse("checkout:form"))
        content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orders/checkout.html")
        self.assertContains(response, self.product.name)
        self.assertContains(response, "₴180")
        self.assertContains(response, "Email для отримання ключа")
        self.assertContains(response, "Цифрова доставка")
        self.assertContains(response, "реальні кошти не списуються")
        self.assertNotIn('name="full_name"', content)
        self.assertNotIn('name="phone"', content)
        self.assertNotIn('name="city"', content)
        self.assertNotIn('name="address"', content)

    def test_checkout_prefills_authenticated_user_email(self) -> None:
        self.login_user()
        self.add_to_cart()

        response = self.client.get(reverse("checkout:form"))

        self.assertContains(
            response,
            'value="checkout-player@example.com"',
            html=False,
        )

    def test_checkout_renders_three_payment_radio_cards(self) -> None:
        self.login_user()
        self.add_to_cart()

        response = self.client.get(reverse("checkout:form"))
        content = response.content.decode()

        self.assertEqual(content.count('type="radio"'), 3)
        self.assertContains(response, "Банківська картка (тест)")
        self.assertContains(response, "Криптовалюта TRC20 (тест)")
        self.assertContains(response, "Google Pay (тест)")
        self.assertNotIn("Оплата при отриманні", content)
        self.assertNotIn("Тестовий баланс", content)
        self.assertNotIn("<select", content)

    def test_valid_checkout_creates_digital_order_and_order_item(self) -> None:
        self.login_user()
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
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.first_name, "")
        self.assertEqual(order.last_name, "")
        self.assertEqual(order.phone, "")
        self.assertEqual(order.city, "")
        self.assertEqual(order.shipping_address, "")
        self.assertEqual(order.email, "olena@example.com")
        self.assertEqual(
            order.payment_method,
            Order.PaymentMethod.BANK_CARD_TEST,
        )
        self.assertEqual(order.total_price, Decimal("180.00"))
        self.assertEqual(order_item.order, order)
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price, Decimal("90.00"))

    def test_valid_checkout_decreases_stock(self) -> None:
        self.login_user()
        self.add_to_cart(quantity=3)

        self.client.post(reverse("checkout:form"), self.checkout_data())

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)

    def test_valid_checkout_clears_session_cart(self) -> None:
        self.login_user()
        self.add_to_cart()

        self.client.post(reverse("checkout:form"), self.checkout_data())

        self.assertNotIn(CART_SESSION_KEY, self.client.session)

    def test_checkout_rejects_quantity_above_latest_stock(self) -> None:
        self.login_user()
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

    def test_checkout_rejects_inactive_product_from_cart(self) -> None:
        self.login_user()
        self.add_to_cart()
        Product.objects.filter(pk=self.product.pk).update(is_active=False)

        response = self.client.post(
            reverse("checkout:form"),
            self.checkout_data(),
        )

        self.assertRedirects(response, reverse("cart:detail"))
        self.assertFalse(Order.objects.exists())
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)

    def test_success_page_renders_order_number_and_total(self) -> None:
        self.login_user()
        self.add_to_cart()
        self.client.post(reverse("checkout:form"), self.checkout_data())
        order = Order.objects.get()

        response = self.client.get(
            reverse("checkout:success", args=[order.pk]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "orders/checkout_success.html")
        self.assertContains(response, f"Замовлення №{order.pk}")
        self.assertContains(response, "Ваші тестові ключі активації")
        self.assertContains(
            response,
            "XXXXX-XXXXX-XXXXX",
            count=2,
        )
        self.assertContains(response, "₴180")

    def test_success_page_is_owner_only(self) -> None:
        self.login_user()
        self.add_to_cart()
        self.client.post(reverse("checkout:form"), self.checkout_data())
        order = Order.objects.get()
        other_user = get_user_model().objects.create_user(
            username="other-checkout-player",
            password="StrongPassword123!",
        )
        other_client = Client()
        other_client.force_login(other_user)
        session = other_client.session
        session["last_checkout_order_id"] = order.pk
        session.save()

        response = other_client.get(
            reverse("checkout:success", args=[order.pk]),
        )

        self.assertEqual(response.status_code, 404)

    def test_checkout_uses_ukrainian_by_default(self) -> None:
        self.login_user()
        self.add_to_cart()

        response = self.client.get(reverse("checkout:form"))

        self.assertContains(response, '<html lang="uk">')
        self.assertContains(response, "Оформлення замовлення")
        self.assertContains(response, "Email для отримання ключа")
        self.assertContains(response, "Підтвердити замовлення")

    def test_checkout_can_be_rendered_in_english(self) -> None:
        self.login_user()
        self.add_to_cart()

        response = self.client.get(
            reverse("checkout:form"),
            HTTP_ACCEPT_LANGUAGE="en",
        )

        self.assertContains(response, '<html lang="en">')
        self.assertContains(response, "Checkout")
        self.assertContains(response, "Email for digital key delivery")
        self.assertContains(response, "Bank card (test)")
        self.assertContains(response, "TRC20 cryptocurrency (test)")
        self.assertContains(response, "Google Pay (test)")
        self.assertContains(response, "Digital delivery")
        self.assertContains(response, "no real funds are charged")
        self.assertContains(response, "Confirm order")


class OrderItemActivationKeyTests(TestCase):
    def test_demo_keys_match_purchased_quantity(self) -> None:
        category = Category.objects.create(
            name="Keys",
            slug="keys",
        )
        product = Product.objects.create(
            name="Key Test Game",
            slug="key-test-game",
            description="Test game.",
            price=Decimal("100.00"),
            category=category,
            platform=Product.Platform.PC,
            stock=10,
        )
        order = Order.objects.create(
            total_price=Decimal("300.00"),
            first_name="",
            last_name="",
            email="keys@example.com",
            phone="",
            city="",
            shipping_address="",
            payment_method=Order.PaymentMethod.BANK_CARD_TEST,
        )
        item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=3,
            price=Decimal("100.00"),
        )

        self.assertEqual(
            item.demo_activation_keys,
            (
                "XXXXX-XXXXX-XXXXX",
                "XXXXX-XXXXX-XXXXX",
                "XXXXX-XXXXX-XXXXX",
            ),
        )
