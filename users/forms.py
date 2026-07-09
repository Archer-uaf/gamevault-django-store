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

from users.models import UserProfile

USERNAME_HELP_TEXT = _("До 15 символів. Дозволені літери, цифри та @/./+/-/_.")


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
        username_field = self.fields["username"]
        username_field.max_length = 15
        username_field.help_text = USERNAME_HELP_TEXT
        username_field.widget.attrs["maxlength"] = 15
        self.fields["password1"].label = _("Пароль")
        self.fields["password2"].label = _("Підтвердження пароля")

    def clean_username(self) -> str:
        """Limit public usernames to a short storefront-friendly value."""
        username = self.cleaned_data["username"]
        if len(username) > 15:
            raise forms.ValidationError(
                _("Ім’я користувача має містити не більше 15 символів."),
                code="username_too_long",
            )
        return username


class AccountAuthenticationForm(AuthenticationForm):
    """Authenticate by username or email while keeping Django's session login."""

    username = forms.CharField(label=_("Ім’я користувача або email"))
    password = forms.CharField(
        label=_("Пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    def clean(self) -> dict[str, Any]:
        """Resolve a submitted email address to the matching username."""
        identifier = self.cleaned_data.get("username")
        if identifier and "@" in identifier:
            user = (
                get_user_model()
                ._default_manager.filter(email__iexact=identifier)
                .order_by("pk")
                .first()
            )
            if user is not None:
                self.cleaned_data["username"] = user.get_username()
        return super().clean()


class AccountPasswordChangeForm(PasswordChangeForm):
    """Use Ukrainian source labels on the password change form."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["old_password"].label = _("Поточний пароль")
        self.fields["new_password1"].label = _("Новий пароль")
        self.fields["new_password2"].label = _("Підтвердження нового пароля")


class ProfileUpdateForm(forms.ModelForm):
    """Update Django user details and the related delivery profile."""

    first_name = forms.CharField(label=_("Ім’я"), max_length=150, required=False)
    last_name = forms.CharField(label=_("Прізвище"), max_length=150, required=False)
    email = forms.EmailField(label=_("Електронна пошта"), required=True)

    class Meta:
        model = UserProfile
        fields = ("phone", "city", "address")
        labels = {
            "phone": _("Телефон"),
            "city": _("Місто"),
            "address": _("Адреса доставки"),
        }
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(
        self,
        *args: Any,
        user: Any,
        **kwargs: Any,
    ) -> None:
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["first_name"].initial = user.first_name
        self.fields["last_name"].initial = user.last_name
        self.fields["email"].initial = user.email

    def save(self, commit: bool = True) -> UserProfile:
        """Persist account fields together with the profile."""
        profile = super().save(commit=False)
        self.user.first_name = self.cleaned_data["first_name"]
        self.user.last_name = self.cleaned_data["last_name"]
        self.user.email = self.cleaned_data["email"]
        if commit:
            self.user.save(update_fields=("first_name", "last_name", "email"))
            profile.save()
        return profile
