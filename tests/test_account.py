from decimal import Decimal
from typing import Any

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from orders.models import Order


class AccountFlowTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="player",
            email="player@example.com",
            password="StrongPassword123!",
        )

    def test_register_page_opens(self) -> None:
        response = self.client.get(reverse("account:register"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")

    def test_user_can_register_and_is_logged_in(self) -> None:
        response = self.client.post(
            reverse("account:register"),
            {
                "username": "new-player",
                "email": "new-player@example.com",
                "password1": "AnotherStrongPassword123!",
                "password2": "AnotherStrongPassword123!",
            },
        )

        self.assertRedirects(response, reverse("account:dashboard"))
        self.assertTrue(
            get_user_model().objects.filter(
                username="new-player",
                email="new-player@example.com",
            ).exists()
        )
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_page_opens(self) -> None:
        response = self.client.get(reverse("account:login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/login.html")

    def test_user_can_login(self) -> None:
        response = self.client.post(
            reverse("account:login"),
            {"username": "player", "password": "StrongPassword123!"},
        )

        self.assertRedirects(response, reverse("account:dashboard"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_user_can_logout(self) -> None:
        self.client.force_login(self.user)

        response = self.client.post(reverse("account:logout"))

        self.assertRedirects(response, reverse("home"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_dashboard_requires_login(self) -> None:
        response = self.client.get(reverse("account:dashboard"))

        self.assertRedirects(
            response,
            f"{reverse('account:login')}?next={reverse('account:dashboard')}",
        )

    def test_authenticated_user_can_see_dashboard(self) -> None:
        self.client.force_login(self.user)

        response = self.client.get(reverse("account:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.user.email)

    def test_profile_page_requires_login(self) -> None:
        response = self.client.get(reverse("account:profile"))

        self.assertRedirects(
            response,
            f"{reverse('account:login')}?next={reverse('account:profile')}",
        )

    def test_authenticated_user_can_open_profile_page(self) -> None:
        self.client.force_login(self.user)

        response = self.client.get(reverse("account:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")
        self.assertContains(response, self.user.email)

    def test_authenticated_user_can_update_profile(self) -> None:
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("account:profile"),
            {
                "username": "digital-player",
                "email": "digital-player@example.com",
            },
        )

        self.assertRedirects(response, reverse("account:profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "digital-player")
        self.assertEqual(self.user.email, "digital-player@example.com")

    def test_profile_page_hides_physical_delivery_fields(self) -> None:
        self.client.force_login(self.user)

        response = self.client.get(reverse("account:profile"))

        self.assertContains(response, "Нікнейм")
        self.assertContains(response, "Електронна пошта")
        for field_name in ("phone", "city", "address", "first_name", "last_name"):
            self.assertNotContains(response, f'name="{field_name}"')
        self.assertNotContains(response, "адресу для майбутніх замовлень")

    def test_profile_page_displays_updated_data(self) -> None:
        self.client.force_login(self.user)
        self.user.username = "updated-player"
        self.user.email = "updated-player@example.com"
        self.user.save(update_fields=("username", "email"))

        response = self.client.get(reverse("account:profile"))

        self.assertContains(response, "updated-player")
        self.assertContains(response, "updated-player@example.com")

    def test_profile_page_can_be_rendered_in_english(self) -> None:
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("account:profile"),
            HTTP_ACCEPT_LANGUAGE="en",
        )

        self.assertContains(response, "Edit profile")
        self.assertContains(response, "Save changes")

    def test_order_history_requires_login(self) -> None:
        response = self.client.get(reverse("account:orders"))

        self.assertRedirects(
            response,
            f"{reverse('account:login')}?next={reverse('account:orders')}",
        )

    def test_order_history_contains_only_current_user_orders(self) -> None:
        other_user = get_user_model().objects.create_user(
            username="other-player",
            password="StrongPassword123!",
        )
        own_order = self.create_order(user=self.user, email="player@example.com")
        other_order = self.create_order(user=other_user, email="other@example.com")
        self.client.force_login(self.user)

        response = self.client.get(reverse("account:orders"))

        self.assertContains(response, f"Замовлення №{own_order.pk}")
        self.assertNotContains(response, f"Замовлення №{other_order.pk}")

    def test_order_history_uses_digital_status_labels(self) -> None:
        order = self.create_order(user=self.user, email="player@example.com")
        order.status = Order.Status.SHIPPED
        order.save(update_fields=("status",))
        self.client.force_login(self.user)

        response = self.client.get(reverse("account:orders"))

        self.assertContains(response, "Ключ надіслано")
        self.assertNotContains(response, "Відправлено")

    def test_password_change_page_requires_login(self) -> None:
        response = self.client.get(reverse("account:password"))

        self.assertRedirects(
            response,
            f"{reverse('account:login')}?next={reverse('account:password')}",
        )

    def test_password_change_preserves_authenticated_session(self) -> None:
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("account:password"),
            {
                "old_password": "StrongPassword123!",
                "new_password1": "ChangedStrongPassword123!",
                "new_password2": "ChangedStrongPassword123!",
            },
        )

        self.assertRedirects(response, reverse("account:dashboard"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_account_pages_use_ukrainian_by_default(self) -> None:
        response = self.client.get(reverse("account:login"))

        self.assertContains(response, '<html lang="uk">')
        self.assertContains(response, "Увійти до облікового запису")

    def test_account_pages_can_be_rendered_in_english(self) -> None:
        response = self.client.get(
            reverse("account:login"),
            HTTP_ACCEPT_LANGUAGE="en",
        )

        self.assertContains(response, '<html lang="en">')
        self.assertContains(response, "Log in to your account")

    @staticmethod
    def create_order(*, user: Any, email: str) -> Order:
        return Order.objects.create(
            user=user,
            total_price=Decimal("100.00"),
            first_name="Test",
            last_name="Player",
            email=email,
            phone="+380000000000",
            city="Kyiv",
            shipping_address="Test street, 1",
            payment_method=Order.PaymentMethod.CARD,
        )
