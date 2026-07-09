"""Serializers for authenticated API order creation and history."""

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from orders.models import Order, OrderItem
from products.models import Product


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
        extra_kwargs = {
            "first_name": {"label": _("Ім'я отримувача")},
            "last_name": {"label": _("Прізвище отримувача")},
            "email": {"label": _("Email для отримання ключа")},
            "phone": {"label": _("Телефон для зв'язку щодо замовлення")},
            "city": {"label": _("Регіон акаунта")},
            "shipping_address": {"label": _("Дані для цифрової доставки")},
        }


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
    """Validate and atomically create an authenticated user's order."""

    items = OrderCreateItemSerializer(many=True, allow_empty=False)
    full_name = serializers.CharField(
        max_length=241,
        label=_("Ім'я отримувача цифрового замовлення"),
    )
    email = serializers.EmailField(
        label=_("Email для отримання ключа"),
        help_text=_("Ключ буде надіслано після обробки замовлення."),
    )
    phone = serializers.CharField(
        max_length=30,
        label=_("Телефон для зв'язку щодо замовлення"),
    )
    city = serializers.CharField(
        max_length=120,
        label=_("Регіон акаунта"),
    )
    address = serializers.CharField(
        label=_("Дані для цифрової доставки"),
        help_text=_("Без фізичної доставки. Вкажіть платформу або примітку."),
    )
    payment_method = serializers.ChoiceField(
        choices=(
            (Order.PaymentMethod.CARD, _("Картка (тестова оплата)")),
            (
                Order.PaymentMethod.CASH_ON_DELIVERY,
                _("Оплата після обробки замовлення"),
            ),
            (Order.PaymentMethod.BALANCE_MOCK, _("Тестовий баланс")),
        )
    )

    def validate_full_name(self, value: str) -> str:
        """Require both a first and last name for the order snapshot."""
        full_name = " ".join(value.split())
        if len(full_name.split(maxsplit=1)) < 2:
            raise serializers.ValidationError(
                _("Вкажіть ім'я та прізвище отримувача.")
            )
        return full_name

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
        """Lock products, validate stock, create snapshots, and decrement stock."""
        request = self.context["request"]
        user = request.user
        item_data = validated_data.pop("items")
        first_name, last_name = validated_data.pop("full_name").split(maxsplit=1)
        address = validated_data.pop("address")
        product_ids = [item["product_id"] for item in item_data]

        with transaction.atomic():
            products = list(
                Product.objects.select_for_update().filter(
                    pk__in=product_ids,
                    is_active=True,
                )
            )
            products_by_id = {int(product.pk): product for product in products}
            if products_by_id.keys() != set(product_ids):
                raise serializers.ValidationError(
                    {"items": _("Один або кілька товарів недоступні.")}
                )

            total_price = Decimal("0.00")
            order_items: list[OrderItem] = []
            for item in item_data:
                product = products_by_id[item["product_id"]]
                quantity = item["quantity"]
                if product.stock < quantity:
                    raise serializers.ValidationError(
                        {
                            "items": _(
                                "Недостатньо товару «%(product)s» на складі."
                            )
                            % {"product": product.name}
                        }
                    )

                unit_price = product.final_price
                total_price += unit_price * quantity
                product.stock -= quantity
                order_items.append(
                    OrderItem(
                        product=product,
                        quantity=quantity,
                        price=unit_price,
                    )
                )

            order = Order.objects.create(
                user=user,
                total_price=total_price,
                first_name=first_name,
                last_name=last_name,
                shipping_address=address,
                **validated_data,
            )
            for order_item in order_items:
                order_item.order = order
            OrderItem.objects.bulk_create(order_items)
            for product in products:
                product.save(update_fields=("stock", "updated_at"))

        return order


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
