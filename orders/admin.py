"""Django admin configuration for orders."""

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "total_price",
        "first_name",
        "last_name",
        "created_at",
    )
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("first_name", "last_name", "email", "phone", "user__username")
    readonly_fields = ("created_at", "updated_at")
    inlines = (OrderItemInline,)
    actions = (
        "mark_as_paid",
        "mark_as_shipped",
        "mark_as_delivered",
        "mark_as_cancelled",
    )

    @admin.action(description=_("Позначити вибрані замовлення як оплачені"))
    def mark_as_paid(
        self,
        request: HttpRequest,
        queryset: QuerySet[Order],
    ) -> None:
        queryset.update(status=Order.Status.PAID)

    @admin.action(description=_("Позначити вибрані замовлення як відправлені"))
    def mark_as_shipped(
        self,
        request: HttpRequest,
        queryset: QuerySet[Order],
    ) -> None:
        queryset.update(status=Order.Status.SHIPPED)

    @admin.action(description=_("Позначити вибрані замовлення як доставлені"))
    def mark_as_delivered(
        self,
        request: HttpRequest,
        queryset: QuerySet[Order],
    ) -> None:
        queryset.update(status=Order.Status.DELIVERED)

    @admin.action(description=_("Позначити вибрані замовлення як скасовані"))
    def mark_as_cancelled(
        self,
        request: HttpRequest,
        queryset: QuerySet[Order],
    ) -> None:
        queryset.update(status=Order.Status.CANCELLED)
