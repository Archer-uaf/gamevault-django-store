"""Catalog models for GameVault."""

from decimal import ROUND_HALF_UP, Decimal
from urllib.parse import urlencode

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class Category(models.Model):
    """A category that can be nested under another catalog category."""

    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        """Return the catalog URL filtered by this category."""
        query = urlencode({"category": self.slug})
        catalog_url = reverse("products:product_list")
        return f"{catalog_url}?{query}"


class Product(models.Model):
    """A video game available in the GameVault catalog."""

    class Platform(models.TextChoices):
        PC = "pc", "PC"
        PLAYSTATION = "playstation", "PlayStation"
        XBOX = "xbox", "Xbox"
        NINTENDO_SWITCH = "nintendo_switch", "Nintendo Switch"

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    category = models.ForeignKey(
        Category,
        related_name="products",
        on_delete=models.PROTECT,
    )
    image = models.ImageField(upload_to="products/", blank=True)
    is_active = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)
    platform = models.CharField(max_length=20, choices=Platform.choices)
    developer = models.CharField(max_length=120, blank=True)
    publisher = models.CharField(max_length=120, blank=True)
    release_date = models.DateField(null=True, blank=True)
    discount_percent = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(90)],
    )
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("slug",), name="product_slug_idx"),
            models.Index(fields=("is_active",), name="product_active_idx"),
            models.Index(fields=("platform",), name="product_platform_idx"),
            models.Index(fields=("created_at",), name="product_created_idx"),
        ]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        """Return the public detail URL for this product."""
        return reverse("products:product_detail", kwargs={"slug": self.slug})

    @property
    def has_discount(self) -> bool:
        return self.discount_percent > 0

    @property
    def final_price(self) -> Decimal:
        price = Decimal(str(self.price))
        discount_multiplier = Decimal(100 - self.discount_percent) / Decimal(100)
        return (price * discount_multiplier).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    @property
    def is_in_stock(self) -> bool:
        return self.stock > 0
