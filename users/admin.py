"""Django admin configuration for user profiles."""

from django.contrib import admin

from users.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "city", "created_at", "updated_at")
    list_filter = ("city", "created_at")
    search_fields = ("user__username", "user__email", "phone", "city")
    readonly_fields = ("created_at", "updated_at")
