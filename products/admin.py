"""Django admin configuration for the product catalog."""

from django.contrib import admin
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
        "price",
        "discount_percent",
        "stock",
        "platform",
        "is_active",
        "is_featured",
        "created_at",
    )
    list_filter = (
        "is_active",
        "is_featured",
        "platform",
        "category",
        "created_at",
    )
    search_fields = ("name", "slug", "developer", "publisher")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at")
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
