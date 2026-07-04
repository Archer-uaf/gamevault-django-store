"""Business rules for verified-purchase reviews."""

from orders.models import Order, OrderItem


def user_has_purchased_product(*, user_id: int, product_id: int) -> bool:
    """Return whether a user-linked order contains the given product."""
    return OrderItem.objects.filter(
        order__user_id=user_id,
        product_id=product_id,
    ).exclude(order__status=Order.Status.CANCELLED).exists()
