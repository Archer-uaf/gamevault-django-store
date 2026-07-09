"""Transactional checkout services built on the session cart."""

from collections.abc import Mapping
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


def create_order_from_cart(
    *,
    cart: Cart,
    customer_data: Mapping[str, str],
    user: Any | None,
) -> Order:
    """Create an order and decrease stock under one database transaction."""
    cart_items = cart.get_items()
    if not cart_items:
        raise EmptyCartError

    quantities = {
        int(item.product.pk): item.quantity
        for item in cart_items
    }

    with transaction.atomic():
        products = list(
            Product.objects.select_for_update()
            .filter(pk__in=quantities, is_active=True)
            .select_related("category")
        )
        products_by_id = {int(product.pk): product for product in products}
        if products_by_id.keys() != quantities.keys():
            raise CheckoutStockError

        total_price = Decimal("0.00")
        order_items: list[OrderItem] = []
        for product_id, quantity in quantities.items():
            product = products_by_id[product_id]
            if product.stock < quantity:
                raise CheckoutStockError

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
            first_name=customer_data["first_name"],
            last_name=customer_data["last_name"],
            email=customer_data["email"],
            phone=customer_data["phone"],
            city=customer_data["city"],
            shipping_address=customer_data["shipping_address"],
            payment_method=customer_data["payment_method"],
            comment=customer_data.get("comment", ""),
        )
        for order_item in order_items:
            order_item.order = order
        OrderItem.objects.bulk_create(order_items)
        for product in products:
            product.save(update_fields=("stock", "updated_at"))

    return order
