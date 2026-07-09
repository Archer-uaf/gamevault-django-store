"""Web views for guest checkout and its success page."""

from typing import Any

from django.contrib import messages
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBase
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.views.generic import FormView, TemplateView
from orders.emails import send_order_notifications

from orders.cart import Cart, CartItem
from orders.checkout import (
    CheckoutStockError,
    EmptyCartError,
    create_order_from_cart,
)
from orders.forms import CheckoutForm
from orders.models import Order

LAST_ORDER_SESSION_KEY = "last_checkout_order_id"


class CheckoutView(FormView):
    """Display and process checkout for the current session cart."""

    template_name = "orders/checkout.html"
    form_class = CheckoutForm

    def dispatch(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponseBase:
        if not self._get_cart_items():
            messages.info(
                request,
                _("Ваш кошик порожній. Додайте ігри перед оформленням."),
            )
            return redirect("cart:detail")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        cart = Cart(self.request)
        cart_items = self._get_cart_items()
        context.update(
            {
                "cart_items": cart_items,
                "cart_total": cart.get_total_price(cart_items),
            }
        )
        return context

    def form_valid(self, form: CheckoutForm) -> HttpResponse:
        cart = Cart(self.request)
        user = self.request.user if self.request.user.is_authenticated else None
        try:
            order = create_order_from_cart(
                cart=cart,
                customer_data=form.get_order_fields(),
                user=user,
            )
        except EmptyCartError:
            messages.info(
                self.request,
                _("Ваш кошик порожній. Додайте ігри перед оформленням."),
            )
            return redirect("cart:detail")
        except CheckoutStockError:
            messages.error(
                self.request,
                _(
                    "Залишки товарів змінилися. Перевірте кількість "
                    "у кошику та спробуйте ще раз."
                ),
            )
            return redirect("cart:detail")

        cart.clear()
        send_order_notifications(order)
        self.request.session[LAST_ORDER_SESSION_KEY] = order.pk
        messages.success(
            self.request,
            _(
                "Замовлення №%(number)s успішно створено. "
                "Ключ буде надіслано на email після обробки."
            )
            % {"number": order.pk},
        )
        return redirect("checkout:success", order_id=order.pk)

    def _get_cart_items(self) -> list[CartItem]:
        if not hasattr(self, "_cart_items"):
            self._cart_items = Cart(self.request).get_items()
        return self._cart_items


class CheckoutSuccessView(TemplateView):
    """Show the last order created in the current browser session."""

    template_name = "orders/checkout_success.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs["order_id"]
        if self.request.session.get(LAST_ORDER_SESSION_KEY) != order_id:
            raise Http404
        context["order"] = get_object_or_404(Order, pk=order_id)
        return context
