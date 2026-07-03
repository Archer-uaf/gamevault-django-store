"""Template context shared by cart-aware web pages."""

from django.http import HttpRequest

from orders.cart import Cart


def cart_summary(request: HttpRequest) -> dict[str, int]:
    """Expose the number of units in the session cart to the header."""
    return {"cart_item_count": len(Cart(request))}
