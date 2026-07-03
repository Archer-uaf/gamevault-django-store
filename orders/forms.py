"""Forms used by the session shopping cart."""

from typing import Any

from django import forms
from django.utils.translation import gettext_lazy as _


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
