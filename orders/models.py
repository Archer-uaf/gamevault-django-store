"""Order models for GameVault."""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Order(models.Model):
    """A snapshot of customer and shipping data for a purchase."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        CARD_MOCK = "card_mock", "Card (mock)"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    city = models.CharField(max_length=120)
    shipping_address = models.TextField()
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("user",), name="order_user_idx"),
            models.Index(fields=("status",), name="order_status_idx"),
            models.Index(fields=("created_at",), name="order_created_idx"),
        ]

    def __str__(self) -> str:
        return f"Order #{self.pk}"

    @property
    def is_cancelled(self) -> bool:
        return self.status == self.Status.CANCELLED

    @property
    def can_be_cancelled(self) -> bool:
        return self.status in {self.Status.PENDING, self.Status.PAID}


class OrderItem(models.Model):
    """A product and price snapshot belonging to an order."""

    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.product} × {self.quantity}"

    @property
    def total_price(self) -> Decimal:
        return Decimal(str(self.price)) * self.quantity
