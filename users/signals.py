"""Signal handlers for user profile lifecycle."""

from typing import Any

from django.conf import settings
from django.db.models import Model
from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(
    sender: type[Model],
    instance: Any,
    created: bool,
    **kwargs: Any,
) -> None:
    """Create a profile once for each newly created user."""
    if created:
        UserProfile.objects.create(user=instance)
