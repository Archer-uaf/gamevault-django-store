"""Serializers for the public catalog API."""

from rest_framework import serializers

from products.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    """Expose a catalog category as read-only API data."""

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "parent")
        read_only_fields = fields


class ProductSerializer(serializers.ModelSerializer):
    """Expose an active catalog product with rating aggregates."""

    category = CategorySerializer(read_only=True)
    genres = CategorySerializer(many=True, read_only=True)
    final_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )
    reviews_count = serializers.IntegerField(source="popularity", read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    localized_description = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "description_en",
            "localized_description",
            "price",
            "final_price",
            "category",
            "genres",
            "image",
            "cover_url",
            "platform",
            "developer",
            "publisher",
            "release_date",
            "stock",
            "is_active",
            "discount_percent",
            "created_at",
            "reviews_count",
            "average_rating",
        )
        read_only_fields = fields
