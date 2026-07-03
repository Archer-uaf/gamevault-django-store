"""Django admin configuration for user profiles."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from users.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "user_email",
        "phone",
        "city",
        "created_at",
        "updated_at",
    )
    list_filter = ("city", "created_at")
    search_fields = ("user__username", "user__email", "phone", "city")
    ordering = ("user__username",)
    list_select_related = ("user",)
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description=_("Електронна пошта"), ordering="user__email")
    def user_email(self, profile: UserProfile) -> str:
        return profile.user.email
