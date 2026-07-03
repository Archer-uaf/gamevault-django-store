"""Django admin configuration for the product catalog."""

from django.contrib import admin
from django.db.models import Avg, Count, QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from products.models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "created_at", "updated_at")
    list_filter = ("parent",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("name", "slug", "parent")}),
        (_("Часові позначки"), {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "platform",
        "price",
        "discount_percent",
        "final_price_display",
        "stock",
        "is_active",
        "review_count_display",
        "average_rating_display",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "category",
        "platform",
        "is_active",
        "created_at",
    )
    search_fields = ("name", "description", "developer", "publisher")
    ordering = ("-created_at",)
    list_select_related = ("category",)
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
    actions = ("mark_active", "mark_inactive", "reset_discount")
    fieldsets = (
        (None, {"fields": ("name", "slug", "description", "category", "image")}),
        (
            _("Продажі"),
            {
                "fields": (
                    "price",
                    "discount_percent",
                    "stock",
                    "is_active",
                    "is_featured",
                )
            },
        ),
        (
            _("Відомості про гру"),
            {
                "fields": (
                    "platform",
                    "developer",
                    "publisher",
                    "release_date",
                )
            },
        ),
        (_("Часові позначки"), {"fields": ("created_at", "updated_at")}),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Product]:
        """Annotate review analytics for the product changelist."""
        return super().get_queryset(request).annotate(
            admin_review_count=Count("reviews", distinct=True),
            admin_average_rating=Avg("reviews__rating"),
        )

    @admin.display(description=_("Кінцева ціна"), ordering="price")
    def final_price_display(self, product: Product) -> str:
        return f"₴{product.final_price}"

    @admin.display(
        description=_("Кількість відгуків"),
        ordering="admin_review_count",
    )
    def review_count_display(self, product: Product) -> int:
        return int(getattr(product, "admin_review_count", 0))

    @admin.display(
        description=_("Середня оцінка"),
        ordering="admin_average_rating",
    )
    def average_rating_display(self, product: Product) -> str:
        rating = getattr(product, "admin_average_rating", None)
        return f"{rating:.1f}" if rating is not None else "—"

    @admin.action(description=_("Позначити вибрані товари як активні"))
    def mark_active(
        self,
        request: HttpRequest,
        queryset: QuerySet[Product],
    ) -> None:
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            _("Оновлено товарів: %(count)d.") % {"count": updated},
        )

    @admin.action(description=_("Позначити вибрані товари як неактивні"))
    def mark_inactive(
        self,
        request: HttpRequest,
        queryset: QuerySet[Product],
    ) -> None:
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            _("Оновлено товарів: %(count)d.") % {"count": updated},
        )

    @admin.action(description=_("Скинути знижку для вибраних товарів"))
    def reset_discount(
        self,
        request: HttpRequest,
        queryset: QuerySet[Product],
    ) -> None:
        updated = queryset.update(discount_percent=0)
        self.message_user(
            request,
            _("Оновлено товарів: %(count)d.") % {"count": updated},
        )
