"""Forms used by the session shopping cart."""

from typing import Any

from django import forms
from django.utils.translation import gettext_lazy as _

from orders.models import Order


class CartQuantityForm(forms.Form):
    """Validate a positive quantity against the current product stock."""

    quantity = forms.IntegerField(
        label=_("Кількість"),
        min_value=1,
        widget=forms.NumberInput(attrs={"min": 1}),
    )

    def __init__(
        self,
        *args: Any,
        max_quantity: int,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.max_quantity = max_quantity
        quantity_field = self.fields["quantity"]
        if isinstance(quantity_field, forms.IntegerField):
            quantity_field.max_value = max_quantity
            quantity_field.widget.attrs["max"] = max_quantity

    def clean_quantity(self) -> int:
        """Reject quantities greater than the latest product stock."""
        quantity = self.cleaned_data["quantity"]
        if quantity > self.max_quantity:
            raise forms.ValidationError(
                _("Обрана кількість перевищує доступний залишок."),
                code="exceeds_stock",
            )
        return quantity


class CheckoutForm(forms.Form):
    """Validate contact data for a digital goods checkout."""

    email = forms.EmailField(
        label=_("Електронна пошта"),
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    payment_method = forms.ChoiceField(
        label=_("Спосіб оплати"),
        choices=((Order.PaymentMethod.CARD, Order.PaymentMethod.CARD.label),),
    )
    comment = forms.CharField(
        label=_("Коментар до замовлення"),
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(
        self,
        *args: Any,
        user: Any | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.user = user

    def get_order_fields(self) -> dict[str, str]:
        """Map form field names to the persisted Order snapshot fields."""
        first_name = "Digital"
        last_name = "Customer"
        if self.user is not None and getattr(self.user, "is_authenticated", False):
            first_name = self.user.first_name or self.user.username or first_name
            last_name = self.user.last_name or last_name
        return {
            "first_name": first_name,
            "last_name": last_name,
            "email": self.cleaned_data["email"],
            "phone": "N/A",
            "city": "Digital delivery",
            "shipping_address": "Digital delivery by email",
            "payment_method": self.cleaned_data["payment_method"],
            "comment": self.cleaned_data["comment"],
        }
