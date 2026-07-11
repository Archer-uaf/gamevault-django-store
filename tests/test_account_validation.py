from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django import forms

from users.forms import RegistrationForm
from users.validators import USERNAME_HELP_TEXT


class UsernameValidationTests(TestCase):
    def test_registration_form_uses_custom_nickname_help_text(self) -> None:
        form = RegistrationForm()
        username_field = form.fields["username"]

        assert isinstance(username_field, forms.CharField)

        self.assertEqual(username_field.max_length, 15)
        self.assertEqual(
            str(username_field.help_text),
            str(USERNAME_HELP_TEXT),
        )
        self.assertEqual(
            username_field.widget.attrs["maxlength"],
            "15",
        )

    def test_registration_page_does_not_show_default_django_help_text(self) -> None:
        response = self.client.get(reverse("account:register"))

        self.assertContains(response, str(USERNAME_HELP_TEXT))
        self.assertNotContains(response, "150 або менше символів")
        self.assertNotContains(response, "@/./+/-/_")

    def test_registration_rejects_cyrillic_nickname(self) -> None:
        response = self.client.post(
            reverse("account:register"),
            {
                "username": "гравець",
                "email": "player@example.com",
                "password1": "StrongPassword123!",
                "password2": "StrongPassword123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            get_user_model().objects.filter(email="player@example.com").exists()
        )

    def test_registration_rejects_nickname_longer_than_15_characters(self) -> None:
        response = self.client.post(
            reverse("account:register"),
            {
                "username": "player-name-1234",
                "email": "player@example.com",
                "password1": "StrongPassword123!",
                "password2": "StrongPassword123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            get_user_model().objects.filter(email="player@example.com").exists()
        )

    def test_registration_accepts_allowed_nickname_characters(self) -> None:
        response = self.client.post(
            reverse("account:register"),
            {
                "username": "player._-123",
                "email": "player@example.com",
                "password1": "StrongPassword123!",
                "password2": "StrongPassword123!",
            },
        )

        self.assertRedirects(response, reverse("account:dashboard"))
        self.assertTrue(
            get_user_model().objects.filter(username="player._-123").exists()
        )

    def test_profile_update_rejects_invalid_nickname(self) -> None:
        user = get_user_model().objects.create_user(
            username="player",
            email="player@example.com",
            password="StrongPassword123!",
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse("account:profile"),
            {
                "username": "player+plus",
                "email": "player@example.com",
            },
        )

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.username, "player")


class PasswordAlphabetValidationTests(TestCase):
    def test_password_validator_accepts_printable_ascii_password(self) -> None:
        validate_password("StrongPassword123!")

    def test_password_validator_rejects_cyrillic(self) -> None:
        with self.assertRaises(ValidationError):
            validate_password("StrongПароль123!")

    def test_web_registration_rejects_cyrillic_password(self) -> None:
        response = self.client.post(
            reverse("account:register"),
            {
                "username": "web-player",
                "email": "web-player@example.com",
                "password1": "StrongПароль123!",
                "password2": "StrongПароль123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            get_user_model().objects.filter(username="web-player").exists()
        )

    def test_api_registration_rejects_cyrillic_password(self) -> None:
        client = APIClient()

        response = client.post(
            reverse("api:register"),
            {
                "username": "api-player",
                "email": "api-player@example.com",
                "password": "StrongПароль123!",
                "password_confirm": "StrongПароль123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.json())

    def test_api_registration_rejects_invalid_nickname(self) -> None:
        client = APIClient()

        response = client.post(
            reverse("api:register"),
            {
                "username": "api+player",
                "email": "api-player@example.com",
                "password": "StrongPassword123!",
                "password_confirm": "StrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.json())
