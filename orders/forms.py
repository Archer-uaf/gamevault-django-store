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
    """Validate customer and digital delivery data for a session checkout."""

    PAYMENT_METHOD_CHOICES = (
        (Order.PaymentMethod.CARD, _("Картка (тестова оплата)")),
        (
            Order.PaymentMethod.CASH_ON_DELIVERY,
            _("Оплата після обробки замовлення"),
        ),
        (Order.PaymentMethod.BALANCE_MOCK, _("Тестовий баланс")),
    )

    full_name = forms.CharField(
        label=_("Ім'я отримувача цифрового замовлення"),
        max_length=241,
        widget=forms.TextInput(attrs={"autocomplete": "name"}),
    )
    email = forms.EmailField(
        label=_("Email для отримання ключа"),
        help_text=_("Ключ буде надіслано після обробки замовлення."),
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    phone = forms.CharField(
        label=_("Телефон для зв'язку щодо замовлення"),
        max_length=30,
        widget=forms.TextInput(attrs={"autocomplete": "tel"}),
    )
    city = forms.CharField(
        label=_("Регіон акаунта"),
        max_length=120,
        widget=forms.TextInput(attrs={"autocomplete": "country-name"}),
    )
    address = forms.CharField(
        label=_("Дані для цифрової доставки"),
        help_text=_("Без фізичної доставки. Вкажіть платформу або примітку."),
        widget=forms.Textarea(attrs={"autocomplete": "off", "rows": 3}),
    )
    payment_method = forms.ChoiceField(
        label=_("Спосіб оплати"),
        choices=PAYMENT_METHOD_CHOICES,
    )

    def clean_full_name(self) -> str:
        """Require both first and last name for the order snapshot."""
        full_name = " ".join(self.cleaned_data["full_name"].split())
        if len(full_name.split(maxsplit=1)) < 2:
            raise forms.ValidationError(
                _("Вкажіть ім'я та прізвище отримувача."),
                code="incomplete_name",
            )
        return full_name

    def get_order_fields(self) -> dict[str, str]:
        """Map form field names to the persisted Order snapshot fields."""
        first_name, last_name = self.cleaned_data["full_name"].split(maxsplit=1)
        return {
            "first_name": first_name,
            "last_name": last_name,
            "email": self.cleaned_data["email"],
            "phone": self.cleaned_data["phone"],
            "city": self.cleaned_data["city"],
            "shipping_address": self.cleaned_data["address"],
            "payment_method": self.cleaned_data["payment_method"],
        }
