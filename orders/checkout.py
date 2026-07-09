"""Transactional checkout services built on the session cart."""

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from django.db import transaction

from orders.cart import Cart
from orders.models import Order, OrderItem
from products.models import Product


class EmptyCartError(ValueError):
    """Raised when checkout is requested without valid cart items."""


class CheckoutStockError(ValueError):
    """Raised when products are inactive, missing, or short on stock."""


class ProductUnavailableError(CheckoutStockError):
    """Raised when one or more requested products cannot be purchased."""


class InsufficientStockError(CheckoutStockError):
    """Raised when a product does not have enough available stock."""

    def __init__(self, product_name: str) -> None:
        self.product_name = product_name
        super().__init__(product_name)


@dataclass(frozen=True)
class OrderLine:
    """One product quantity requested for order creation."""

    product_id: int
    quantity: int


def create_order_from_cart(
    *,
    cart: Cart,
    customer_data: Mapping[str, str],
    user: Any | None,
) -> Order:
    """Create an order from the session cart and clear it after success."""
    cart_items = cart.get_items()
    if not cart_items:
        raise EmptyCartError

    order = create_order_from_items(
        items=[
            OrderLine(product_id=int(item.product.pk), quantity=item.quantity)
            for item in cart_items
        ],
        customer_data=customer_data,
        user=user,
    )
    cart.clear()
    return order


def create_order_from_items(
    *,
    items: list[OrderLine],
    customer_data: Mapping[str, str],
    user: Any | None,
) -> Order:
    """Create an order and decrease stock under one database transaction."""
    if not items:
        raise EmptyCartError

    product_ids = [item.product_id for item in items]
    with transaction.atomic():
        products = list(
            Product.objects.select_for_update()
            .filter(pk__in=product_ids, is_active=True)
            .select_related("category")
        )
        products_by_id = {int(product.pk): product for product in products}
        if products_by_id.keys() != set(product_ids):
            raise ProductUnavailableError

        total_price = Decimal("0.00")
        order_items: list[OrderItem] = []
        for item in items:
            product = products_by_id[item.product_id]
            if product.stock < item.quantity:
                raise InsufficientStockError(product.name)

            unit_price = product.final_price
            total_price += unit_price * item.quantity
            product.stock -= item.quantity
            order_items.append(
                OrderItem(
                    product=product,
                    quantity=item.quantity,
                    price=unit_price,
                )
            )

        order = Order.objects.create(
            user=user,
            total_price=total_price,
            first_name=customer_data["first_name"],
            last_name=customer_data["last_name"],
            email=customer_data["email"],
            phone=customer_data["phone"],
            city=customer_data["city"],
            shipping_address=customer_data["shipping_address"],
            payment_method=customer_data["payment_method"],
        )
        for order_item in order_items:
            order_item.order = order
        OrderItem.objects.bulk_create(order_items)
        for product in products:
            product.save(update_fields=("stock", "updated_at"))

    return order
