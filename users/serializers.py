"""Serializers for API registration and current-user data."""

from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()
USERNAME_HELP_TEXT = _("До 15 символів. Дозволені літери, цифри та @/./+/-/_.")


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
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message=_("Користувач із таким ім’ям вже існує."),
            )
        ],
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
        """Require matching passwords and apply Django password validators."""
        password = attrs.get("password", "")
        if password != attrs.get("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": _("Паролі не збігаються.")}
            )
        try:
            validate_password(password)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                {"password": list(exc.messages)}
            ) from exc
        return attrs

    def create(self, validated_data: dict[str, Any]) -> Any:
        """Create a user while hashing the submitted password."""
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class EmailOrUsernameTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Allow SimpleJWT token login with either username or email."""

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        """Resolve email input to the matching username before authentication."""
        identifier = attrs.get(self.username_field)
        if identifier and "@" in identifier:
            user = (
                User._default_manager.filter(email__iexact=identifier)
                .order_by("pk")
                .first()
            )
            if user is not None:
                attrs[self.username_field] = user.get_username()
        return super().validate(attrs)
