"""Serializers for API registration and current-user data."""

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from users.validators import (
    USERNAME_ERROR_MESSAGE,
    USERNAME_HELP_TEXT,
    username_validator,
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Expose safe identity fields for the authenticated user."""

    class Meta:
        model = User
        fields = ("id", "username", "email")
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    """Validate credentials and create a standard Django user."""

    username = serializers.CharField(
        max_length=15,
        help_text=USERNAME_HELP_TEXT,
        validators=[username_validator],
        error_messages={
            "max_length": USERNAME_ERROR_MESSAGE,
        },
    )
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    password_confirm = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password_confirm")
        read_only_fields = ("id",)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate identity data and apply all Django password validators."""
        username = str(attrs.get("username", "")).strip()
        email = str(attrs.get("email", "")).strip()
        password = attrs.get("password", "")

        if User.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError(
                {"username": _("Цей нікнейм уже використовується.")}
            )

        if password != attrs.get("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": _("Паролі не збігаються.")}
            )

        candidate_user = User(username=username, email=email)
        try:
            validate_password(password, user=candidate_user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                {"password": list(exc.messages)}
            ) from exc

        attrs["username"] = username
        attrs["email"] = email
        return attrs

    def create(self, validated_data: dict[str, Any]) -> Any:
        """Create a user while hashing the submitted password."""
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)
