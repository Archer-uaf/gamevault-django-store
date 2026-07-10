"""Reusable catalog queryset annotations."""

from __future__ import annotations

from decimal import Decimal
from typing import TypeVar

from django.db.models import DecimalField, ExpressionWrapper, F, Model, QuerySet, Value
from django.db.models.functions import Cast


ModelT = TypeVar("ModelT", bound=Model)

EFFECTIVE_PRICE_ANNOTATION = "effective_price"


def effective_price_expression() -> ExpressionWrapper:
    """Return the DB expression for price after discount."""
    percent_field: DecimalField[Decimal, Decimal] = DecimalField(
        max_digits=5,
        decimal_places=2,
    )
    money_field: DecimalField[Decimal, Decimal] = DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    full_percent = Value(Decimal("100.00"), output_field=percent_field)
    discount_percent = Cast(F("discount_percent"), output_field=percent_field)

    return ExpressionWrapper(
        F("price") * ((full_percent - discount_percent) / full_percent),
        output_field=money_field,
    )


def with_effective_price(queryset: QuerySet[ModelT]) -> QuerySet[ModelT]:
    """Annotate a queryset with final price for database-level ordering."""
    return queryset.annotate(
        **{EFFECTIVE_PRICE_ANNOTATION: effective_price_expression()},
    )
