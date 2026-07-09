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
            "username": _("Нікнейм"),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = _("Пароль")
        self.fields["password2"].label = _("Підтвердження пароля")


class AccountAuthenticationForm(AuthenticationForm):
    """Use Ukrainian source labels on the site login form."""

    username = forms.CharField(label=_("Нікнейм"))
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


class ProfileUpdateForm(forms.Form):
    """Update public account details for a digital games store."""

    username = forms.CharField(label=_("Нікнейм"), max_length=150, required=True)
    email = forms.EmailField(label=_("Електронна пошта"), required=True)

    def __init__(
        self,
        *args: Any,
        user: Any,
        **kwargs: Any,
    ) -> None:
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["username"].initial = user.username
        self.fields["email"].initial = user.email

    def clean_username(self) -> str:
        username = str(self.cleaned_data["username"]).strip()
        user_model = get_user_model()
        if (
            user_model.objects.exclude(pk=self.user.pk)
            .filter(username=username)
            .exists()
        ):
            raise forms.ValidationError(
                _("Користувач із таким нікнеймом уже існує.")
            )
        return username

    def save(self) -> Any:
        """Persist account fields used by digital orders."""
        self.user.username = self.cleaned_data["username"]
        self.user.email = self.cleaned_data["email"]
        self.user.save(update_fields=("username", "email"))
        return self.user
