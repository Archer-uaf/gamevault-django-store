"""Web views for authenticated digital checkout and its success page."""

from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBase
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext as _
from django.views.generic import FormView, TemplateView

from orders.cart import Cart, CartItem
from orders.constants import DEMO_ACTIVATION_KEY
from orders.checkout import (
    CheckoutStockError,
    EmptyCartError,
    create_order_from_cart,
)
from orders.emails import send_order_notifications
from orders.forms import CheckoutForm
from orders.models import Order

LAST_ORDER_SESSION_KEY = "last_checkout_order_id"


class CheckoutView(LoginRequiredMixin, FormView):
    """Display and process checkout for an authenticated user."""

    template_name = "orders/checkout.html"
    form_class = CheckoutForm

    def dispatch(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponseBase:
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not self._get_cart_items():
            messages.info(
                request,
                _("Ваш кошик порожній. Додайте ігри перед оформленням."),
            )
            return redirect("cart:detail")
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self) -> dict[str, Any]:
        """Prefill the delivery email from the authenticated account."""
        initial = super().get_initial()
        email = getattr(self.request.user, "email", "")
        if email:
            initial["email"] = email
        initial["payment_method"] = Order.PaymentMethod.BANK_CARD_TEST
        return initial

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
        try:
            order = create_order_from_cart(
                cart=cart,
                customer_data=form.get_order_fields(),
                user=self.request.user,
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

        send_order_notifications(order)
        self.request.session[LAST_ORDER_SESSION_KEY] = order.pk
        messages.success(
            self.request,
            _(
                "Замовлення №%(number)s успішно створено. "
                "Ключ буде надіслано на вказаний email."
            )
            % {"number": order.pk},
        )
        return redirect("checkout:success", order_id=order.pk)

    def _get_cart_items(self) -> list[CartItem]:
        if not hasattr(self, "_cart_items"):
            self._cart_items = Cart(self.request).get_items()
        return self._cart_items


class CheckoutSuccessView(LoginRequiredMixin, TemplateView):
    """Show the authenticated user's last checkout order."""

    template_name = "orders/checkout_success.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs["order_id"]
        if self.request.session.get(LAST_ORDER_SESSION_KEY) != order_id:
            raise Http404
        context["order"] = get_object_or_404(
            Order.objects.prefetch_related("items__product"),
            pk=order_id,
            user=self.request.user,
        )
        context["demo_activation_key"] = DEMO_ACTIVATION_KEY
        return context
