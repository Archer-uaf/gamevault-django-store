"""Serializers for authenticated API order creation and history."""

from typing import Any

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from orders.checkout import (
    EmptyCartError,
    InsufficientStockError,
    OrderLine,
    ProductUnavailableError,
    create_order_from_items,
)
from orders.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """Expose the product snapshot stored in an order item."""

    product_id = serializers.IntegerField(read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product_id",
            "product_name",
            "quantity",
            "price",
            "total_price",
        )
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    """Expose an authenticated user's order and its items."""

    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(
        source="digital_status_display",
        read_only=True,
        label=_("Статус цифрового замовлення"),
    )
    payment_method_display = serializers.CharField(
        source="digital_payment_method_display",
        read_only=True,
        label=_("Спосіб оплати"),
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "status_display",
            "total_price",
            "first_name",
            "last_name",
            "email",
            "phone",
            "city",
            "shipping_address",
            "payment_method",
            "payment_method_display",
            "created_at",
            "items",
        )
        read_only_fields = fields


class OrderCreateItemSerializer(serializers.Serializer):
    """Validate one product and quantity in an API order request."""

    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class OrderCreateSerializer(serializers.Serializer):
    """Validate and atomically create an authenticated digital order."""

    items = OrderCreateItemSerializer(many=True, allow_empty=False)
    email = serializers.EmailField(label=_("Email для отримання ключа"))
    payment_method = serializers.ChoiceField(
        choices=Order.PaymentMethod.choices,
        label=_("Спосіб оплати"),
    )

    def validate_items(self, value: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Reject duplicate product ids in one order payload."""
        product_ids = [item["product_id"] for item in value]
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError(
                _(
                    "Кожен товар можна вказати в замовленні "
                    "лише один раз."
                )
            )
        return value

    def create(self, validated_data: dict[str, Any]) -> Order:
        """Create an order through the shared checkout service."""
        request = self.context["request"]
        item_data = validated_data.pop("items")
        customer_data = {
            "first_name": "",
            "last_name": "",
            "email": str(validated_data["email"]),
            "phone": "",
            "city": "",
            "shipping_address": "",
            "payment_method": str(validated_data["payment_method"]),
        }
        items = [
            OrderLine(
                product_id=int(item["product_id"]),
                quantity=int(item["quantity"]),
            )
            for item in item_data
        ]

        try:
            return create_order_from_items(
                items=items,
                customer_data=customer_data,
                user=request.user,
            )
        except EmptyCartError as error:
            raise serializers.ValidationError(
                {"items": _("Список товарів не може бути порожнім.")}
            ) from error
        except ProductUnavailableError as error:
            raise serializers.ValidationError(
                {"items": _("Один або кілька товарів недоступні.")}
            ) from error
        except InsufficientStockError as error:
            raise serializers.ValidationError(
                {
                    "items": _(
                        "Недостатньо товару «%(product)s» на складі."
                    )
                    % {"product": error.product_name}
                }
            ) from error


class CartAddItemSerializer(serializers.Serializer):
    """Validate a product addition to the session cart."""

    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1, default=1)


class CartUpdateItemSerializer(serializers.Serializer):
    """Validate a cart item quantity update."""

    quantity = serializers.IntegerField(min_value=1)


class CartProductOutputSerializer(serializers.Serializer):
    """Expose the product data embedded in one cart row."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.SlugField()


class CartItemOutputSerializer(serializers.Serializer):
    """Expose one session cart row."""

    product = CartProductOutputSerializer()
    quantity = serializers.IntegerField()
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    is_available = serializers.BooleanField()


class CartOutputSerializer(serializers.Serializer):
    """Expose the full session cart state."""

    items = CartItemOutputSerializer(many=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_items = serializers.IntegerField()
