"""Django admin configuration for orders."""

from decimal import Decimal
from typing import Any

from django.contrib import admin
from django.db.models import Count, Q, QuerySet, Sum
from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _

from orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ("product", "quantity", "price")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_list_template = "admin/orders/order/change_list.html"
    list_display = (
        "id",
        "customer_name",
        "email",
        "user",
        "status",
        "payment_method",
        "total_price",
        "created_at",
    )
    list_filter = ("status", "payment_method", "created_at")
    search_fields = (
        "=id",
        "email",
        "first_name",
        "last_name",
        "phone",
        "user__username",
        "user__email",
    )
    ordering = ("-created_at",)
    list_select_related = ("user",)
    readonly_fields = ("created_at", "updated_at")
    inlines = (OrderItemInline,)
    actions = (
        "mark_as_paid",
        "mark_as_shipped",
        "mark_as_delivered",
        "mark_as_cancelled",
    )

    @admin.display(description=_("Покупець"), ordering="first_name")
    def customer_name(self, order: Order) -> str:
        full_name = f"{order.first_name} {order.last_name}".strip()
        return full_name or order.email

    def get_readonly_fields(
        self,
        request: HttpRequest,
        obj: Order | None = None,
    ) -> tuple[str, ...]:
        """Protect order snapshots after the order has been created."""
        if obj is None:
            return self.readonly_fields
        return (
            "user",
            "total_price",
            "first_name",
            "last_name",
            "email",
            "phone",
            "city",
            "shipping_address",
            "payment_method",
            "created_at",
            "updated_at",
        )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Order]:
        """Load the optional account relation with each order row."""
        return super().get_queryset(request).select_related("user")

    def changelist_view(
        self,
        request: HttpRequest,
        extra_context: dict[str, Any] | None = None,
    ) -> HttpResponse:
        """Add aggregate order metrics to the standard changelist."""
        revenue_statuses = (
            Order.Status.PAID,
            Order.Status.SHIPPED,
            Order.Status.DELIVERED,
        )
        summary = self.get_queryset(request).aggregate(
            total_orders=Count("id"),
            total_revenue=Sum(
                "total_price",
                filter=Q(status__in=revenue_statuses),
            ),
            pending_orders=Count(
                "id",
                filter=Q(status=Order.Status.PENDING),
            ),
            paid_orders=Count(
                "id",
                filter=Q(status=Order.Status.PAID),
            ),
        )
        summary["total_revenue"] = summary["total_revenue"] or Decimal("0.00")
        context = {**(extra_context or {}), "order_summary": summary}
        return super().changelist_view(request, extra_context=context)

    @admin.action(description=_("Позначити вибрані замовлення як оплачені"))
    def mark_as_paid(
        self,
        request: HttpRequest,
        queryset: QuerySet[Order],
    ) -> None:
        updated = queryset.filter(status=Order.Status.PENDING).update(
            status=Order.Status.PAID
        )
        self._report_updated(request, updated)

    @admin.action(description=_("Позначити вибрані замовлення як ключ надіслано"))
    def mark_as_shipped(
        self,
        request: HttpRequest,
        queryset: QuerySet[Order],
    ) -> None:
        updated = queryset.filter(status=Order.Status.PAID).update(
            status=Order.Status.SHIPPED
        )
        self._report_updated(request, updated)

    @admin.action(description=_("Позначити вибрані замовлення як виконані"))
    def mark_as_delivered(
        self,
        request: HttpRequest,
        queryset: QuerySet[Order],
    ) -> None:
        updated = queryset.filter(status=Order.Status.SHIPPED).update(
            status=Order.Status.DELIVERED
        )
        self._report_updated(request, updated)

    @admin.action(description=_("Позначити вибрані замовлення як скасовані"))
    def mark_as_cancelled(
        self,
        request: HttpRequest,
        queryset: QuerySet[Order],
    ) -> None:
        updated = queryset.filter(
            status__in=(Order.Status.PENDING, Order.Status.PAID)
        ).update(status=Order.Status.CANCELLED)
        self._report_updated(request, updated)

    def _report_updated(self, request: HttpRequest, updated: int) -> None:
        self.message_user(
            request,
            _("Оновлено замовлень: %(count)d.") % {"count": updated},
        )
