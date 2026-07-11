"""Filters for the public catalog API."""

from typing import Any

from django.db.models import Q, QuerySet
from django_filters import rest_framework as filters

from products.models import Product


class ProductFilter(filters.FilterSet):
    """Filter products by category, platform, and price range."""

    category = filters.CharFilter(method="filter_category")
    platform = filters.ChoiceFilter(choices=Product.Platform.choices)
    price_min = filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Product
        fields: tuple[str, ...] = ()

    def filter_category(
        self,
        queryset: QuerySet[Product],
        name: str,
        value: Any,
    ) -> QuerySet[Product]:
        """Accept either a numeric category id or a category slug."""
        category = str(value).strip()
        if category.isdigit():
            category_id = int(category)
            return queryset.filter(
                Q(category_id=category_id) | Q(genres__id=category_id)
            ).distinct()
        return queryset.filter(
            Q(category__slug=category) | Q(genres__slug=category)
        ).distinct()
