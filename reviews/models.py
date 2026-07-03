"""Review models for GameVault."""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    """A user's rating and comment for one catalog product."""

    product = models.ForeignKey(
        "products.Product",
        related_name="reviews",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="reviews",
        on_delete=models.CASCADE,
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("product", "user"),
                name="unique_review_product_user",
            )
        ]
        indexes = [
            models.Index(fields=("product",), name="review_product_idx"),
            models.Index(fields=("user",), name="review_user_idx"),
            models.Index(fields=("rating",), name="review_rating_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.product}: {self.rating}/5 by {self.user}"
