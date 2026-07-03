"""Session-backed shopping cart services."""

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal
from typing import TypedDict

from django.contrib.sessions.backends.base import SessionBase
from django.http import HttpRequest

from products.models import Product

CART_SESSION_KEY = "cart"


class CartEntry(TypedDict):
    """Serializable data stored for one product in the session."""

    quantity: int


@dataclass(frozen=True, slots=True)
class CartItem:
    """One rendered cart row with current catalog pricing."""

    product: Product
    quantity: int
    unit_price: Decimal
    total_price: Decimal

    @property
    def is_available(self) -> bool:
        """Return whether the requested quantity is currently in stock."""
        return self.product.is_active and self.quantity <= self.product.stock


class Cart:
    """Manage cart quantities in the current Django session."""

    def __init__(self, request: HttpRequest) -> None:
        self.session: SessionBase = request.session
        stored_cart = self.session.get(CART_SESSION_KEY, {})
        self._data: dict[str, CartEntry] = (
            stored_cart if isinstance(stored_cart, dict) else {}
        )

    def add(self, product: Product, quantity: int = 1) -> None:
        """Add a quantity to a product already present in the cart."""
        product_key = str(product.pk)
        current_quantity = self._get_quantity(product_key)
        self._set_quantity(product, current_quantity + quantity)

    def update(self, product: Product, quantity: int) -> None:
        """Replace the quantity for one product in the cart."""
        self._set_quantity(product, quantity)

    def remove(self, product: Product) -> None:
        """Remove a product from the cart if it is present."""
        product_key = str(product.pk)
        if product_key in self._data:
            del self._data[product_key]
            self._save()

    def clear(self) -> None:
        """Remove all cart data from the current session."""
        if CART_SESSION_KEY in self.session:
            del self.session[CART_SESSION_KEY]
            self.session.modified = True
        self._data = {}

    def get_items(self) -> list[CartItem]:
        """Return valid cart rows using current product data and prices."""
        product_ids = [
            int(product_key)
            for product_key in self._data
            if product_key.isdigit()
        ]
        products = Product.objects.filter(
            pk__in=product_ids,
            is_active=True,
        ).select_related("category")
        products_by_id = {str(product.pk): product for product in products}

        items: list[CartItem] = []
        invalid_keys: list[str] = []
        for product_key, entry in self._data.items():
            product = products_by_id.get(product_key)
            quantity = entry.get("quantity") if isinstance(entry, dict) else None
            if product is None or not isinstance(quantity, int) or quantity < 1:
                invalid_keys.append(product_key)
                continue

            unit_price = product.final_price
            items.append(
                CartItem(
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=unit_price * quantity,
                )
            )

        if invalid_keys:
            for product_key in invalid_keys:
                self._data.pop(product_key, None)
            self._save()

        return items

    def get_total_price(
        self,
        items: Iterable[CartItem] | None = None,
    ) -> Decimal:
        """Calculate the cart total from current discounted prices."""
        cart_items = items if items is not None else self.get_items()
        return sum(
            (item.total_price for item in cart_items),
            start=Decimal("0.00"),
        )

    def __len__(self) -> int:
        """Return the total number of product units in the session cart."""
        return sum(
            entry.get("quantity", 0)
            for entry in self._data.values()
            if isinstance(entry, dict)
            and isinstance(entry.get("quantity"), int)
            and entry["quantity"] > 0
        )

    def _get_quantity(self, product_key: str) -> int:
        entry = self._data.get(product_key)
        if not isinstance(entry, dict):
            return 0
        quantity = entry.get("quantity")
        return quantity if isinstance(quantity, int) and quantity > 0 else 0

    def _set_quantity(self, product: Product, quantity: int) -> None:
        if quantity < 1:
            raise ValueError("Cart quantity must be positive.")
        if quantity > product.stock:
            raise ValueError("Cart quantity exceeds available stock.")

        self._data[str(product.pk)] = {"quantity": quantity}
        self._save()

    def _save(self) -> None:
        self.session[CART_SESSION_KEY] = self._data
        self.session.modified = True
