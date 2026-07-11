"""Custom validation rules for GameVault accounts."""

from typing import Any

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


USERNAME_HELP_TEXT = _(
    "Нікнейм має містити не більше 15 символів. "
    "Дозволені лише латинські літери, цифри та символи «.», «-» і «_»."
)
USERNAME_ERROR_MESSAGE = _(
    "Введіть нікнейм довжиною до 15 символів, використовуючи лише "
    "латинські літери, цифри та символи «.», «-» і «_»."
)

username_validator = RegexValidator(
    regex=r"^[A-Za-z0-9._-]+\Z",
    message=USERNAME_ERROR_MESSAGE,
    code="invalid_username",
)


class ASCIIPrintablePasswordValidator:
    """Allow printable ASCII characters except spaces in passwords."""

    message = _(
        "Пароль може містити лише латинські літери, цифри та "
        "спеціальні символи без пробілів."
    )

    def validate(self, password: str, user: Any = None) -> None:
        """Reject non-ASCII characters, spaces and control characters."""
        if not password or any(
            not 33 <= ord(character) <= 126 for character in password
        ):
            raise ValidationError(
                self.message,
                code="password_not_ascii_printable",
            )

    def get_help_text(self) -> str:
        """Return the rule displayed by Django forms."""
        return str(self.message)
