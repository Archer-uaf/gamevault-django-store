"""Order models for GameVault."""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Order(models.Model):
    """A snapshot of customer and digital delivery data for a purchase."""

    class Status(models.TextChoices):
        PENDING = "pending", _("Очікує обробки")
        PAID = "paid", _("Оплачено")
        SHIPPED = "shipped", _("Відправлено")
        DELIVERED = "delivered", _("Доставлено")
        CANCELLED = "cancelled", _("Скасовано")

    class PaymentMethod(models.TextChoices):
        BANK_CARD_TEST = "bank_card_test", _("Банківська картка (тест)")
        CRYPTO_TRC20_TEST = (
            "crypto_trc20_test",
            _("Криптовалюта TRC20 (тест)"),
        )
        GOOGLE_PAY_TEST = "google_pay_test", _("Google Pay (тест)")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True,
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
        constraints = [
            models.CheckConstraint(
                condition=models.Q(total_price__gte=0),
                name="order_total_price_non_negative",
            ),
        ]
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

    @property
    def digital_status_display(self) -> str:
        labels = {
            self.Status.PENDING.value: _("Очікує обробки"),
            self.Status.PAID.value: _("Оплачено"),
            self.Status.SHIPPED.value: _("Ключ надіслано"),
            self.Status.DELIVERED.value: _("Виконано"),
            self.Status.CANCELLED.value: _("Скасовано"),
        }
        return str(labels.get(self.status, self.get_status_display()))

    @property
    def digital_payment_method_display(self) -> str:
        labels = {
            self.PaymentMethod.BANK_CARD_TEST.value: _(
                "Банківська картка (тест)"
            ),
            self.PaymentMethod.CRYPTO_TRC20_TEST.value: _(
                "Криптовалюта TRC20 (тест)"
            ),
            self.PaymentMethod.GOOGLE_PAY_TEST.value: _("Google Pay (тест)"),
            # Temporary compatibility for orders created before migration 0004.
            "card": _("Банківська картка (старий тестовий запис)"),
            "cash_on_delivery": _(
                "Банківська картка (старий тестовий запис)"
            ),
            "balance_mock": _("Банківська картка (старий тестовий запис)"),
        }
        return str(
            labels.get(self.payment_method, self.get_payment_method_display())
        )


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

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name="order_item_price_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="order_item_quantity_positive",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.product} × {self.quantity}"

    @property
    def total_price(self) -> Decimal:
        return Decimal(str(self.price)) * self.quantity
