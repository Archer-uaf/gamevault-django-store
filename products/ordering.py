"""Ordering helpers for the catalog API."""

from typing import Any

from django.db.models import QuerySet
from rest_framework.filters import OrderingFilter
from rest_framework.request import Request

from products.querysets import EFFECTIVE_PRICE_ANNOTATION


class EffectivePriceOrderingFilter(OrderingFilter):
    """Map public price ordering to the effective price annotation."""

    def remove_invalid_fields(
        self,
        queryset: QuerySet[Any],
        fields: list[str],
        view: Any,
        request: Request,
    ) -> list[str]:
        valid_fields = super().remove_invalid_fields(
            queryset,
            fields,
            view,
            request,
        )
        return [self._map_price_field(field) for field in valid_fields]

    @staticmethod
    def _map_price_field(field: str) -> str:
        if field == "price":
            return EFFECTIVE_PRICE_ANNOTATION
        if field == "-price":
            return f"-{EFFECTIVE_PRICE_ANNOTATION}"
        return field
