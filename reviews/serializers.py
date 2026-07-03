"""Serializers for public and verified-purchase review API operations."""

from typing import Any

from django.db import IntegrityError, transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from products.models import Product
from reviews.models import Review
from reviews.services import user_has_purchased_product


class ReviewSerializer(serializers.ModelSerializer):
    """Expose reviews publicly and validate verified-purchase creation."""

    product = serializers.IntegerField(source="product_id", read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source="product",
        queryset=Product.objects.filter(is_active=True),
        write_only=True,
    )
    user = serializers.CharField(source="user.username", read_only=True)
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(allow_blank=False, trim_whitespace=True)

    class Meta:
        model = Review
        fields = (
            "id",
            "product",
            "product_id",
            "user",
            "rating",
            "comment",
            "created_at",
        )
        read_only_fields = ("id", "product", "user", "created_at")

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Require a purchase and reject an existing user review."""
        request = self.context["request"]
        user_id = request.user.pk
        product = attrs["product"]
        if user_id is None:
            raise serializers.ValidationError(_("Потрібна автентифікація."))
        if not user_has_purchased_product(
            user_id=user_id,
            product_id=product.pk,
        ):
            raise serializers.ValidationError(
                _("Залишити відгук можна лише після покупки цієї гри.")
            )
        if Review.objects.filter(product=product, user_id=user_id).exists():
            raise serializers.ValidationError(
                _("Ви вже опублікували відгук про цю гру.")
            )
        return attrs

    def create(self, validated_data: dict[str, Any]) -> Review:
        """Create a review while handling a concurrent duplicate safely."""
        try:
            with transaction.atomic():
                return Review.objects.create(**validated_data)
        except IntegrityError as exc:
            raise serializers.ValidationError(
                _("Ви вже опублікували відгук про цю гру.")
            ) from exc
