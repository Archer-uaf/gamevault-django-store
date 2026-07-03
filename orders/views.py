"""Web views for the session shopping cart."""

from typing import Any

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import TemplateView

from orders.cart import Cart
from orders.forms import CartQuantityForm
from products.models import Product


class CartDetailView(TemplateView):
    """Display products stored in the current session cart."""

    template_name = "orders/cart_detail.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        items = cart.get_items()
        context.update(
            {
                "cart_items": items,
                "cart_total": cart.get_total_price(items),
            }
        )
        return context


class CartAddView(View):
    """Add an active catalog product to the session cart."""

    http_method_names = ["post"]

    def post(
        self,
        request: HttpRequest,
        product_id: int,
    ) -> HttpResponse:
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        form = CartQuantityForm(request.POST, max_quantity=product.stock)
        if not form.is_valid():
            messages.error(request, _stock_error_message(product))
            return redirect(product.get_absolute_url())

        cart = Cart(request)
        try:
            cart.add(product, form.cleaned_data["quantity"])
        except ValueError:
            messages.error(request, _stock_error_message(product))
        else:
            messages.success(
                request,
                _("«%(product)s» додано до кошика.") % {"product": product.name},
            )
        return redirect(product.get_absolute_url())


class CartUpdateView(View):
    """Replace the quantity of one product in the session cart."""

    http_method_names = ["post"]

    def post(
        self,
        request: HttpRequest,
        product_id: int,
    ) -> HttpResponse:
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        form = CartQuantityForm(request.POST, max_quantity=product.stock)
        if not form.is_valid():
            messages.error(request, _stock_error_message(product))
            return redirect("cart:detail")

        try:
            Cart(request).update(product, form.cleaned_data["quantity"])
        except ValueError:
            messages.error(request, _stock_error_message(product))
        else:
            messages.success(
                request,
                _("Кількість «%(product)s» оновлено.")
                % {"product": product.name},
            )
        return redirect("cart:detail")


class CartRemoveView(View):
    """Remove one product from the session cart."""

    http_method_names = ["post"]

    def post(
        self,
        request: HttpRequest,
        product_id: int,
    ) -> HttpResponse:
        product = get_object_or_404(Product, pk=product_id)
        Cart(request).remove(product)
        messages.success(
            request,
            _("«%(product)s» видалено з кошика.") % {"product": product.name},
        )
        return redirect("cart:detail")


def _stock_error_message(product: Product) -> str:
    return _("Для «%(product)s» доступно одиниць: %(stock)s.") % {
        "product": product.name,
        "stock": product.stock,
    }
