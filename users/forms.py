"""Forms for the web account authentication flow."""

from typing import Any

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)
from django.utils.translation import gettext_lazy as _


class RegistrationForm(UserCreationForm):
    """Create a Django user with a required email address."""

    email = forms.EmailField(label=_("Електронна пошта"), required=True)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password1", "password2")
        labels = {
            "username": _("Ім’я користувача"),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = _("Пароль")
        self.fields["password2"].label = _("Підтвердження пароля")


class AccountAuthenticationForm(AuthenticationForm):
    """Use Ukrainian source labels on the site login form."""

    username = forms.CharField(label=_("Ім’я користувача"))
    password = forms.CharField(
        label=_("Пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )


class AccountPasswordChangeForm(PasswordChangeForm):
    """Use Ukrainian source labels on the password change form."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["old_password"].label = _("Поточний пароль")
        self.fields["new_password1"].label = _("Новий пароль")
        self.fields["new_password2"].label = _("Підтвердження нового пароля")
