"""Email helpers for order notifications."""

from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import gettext as _

from orders.models import Order


def send_order_confirmation_email(order: Order) -> int:
    """Send a simple order confirmation email to the customer."""
    subject = _("Підтвердження замовлення №%(number)s") % {
        "number": order.pk,
    }
    message = _(
        "Дякуємо за замовлення в GameVault.\n\n"
        "Номер замовлення: %(number)s\n"
        "Сума: ₴%(total)s\n"
        "Статус: %(status)s\n\n"
        "Ми повідомимо вас, коли статус замовлення зміниться."
    ) % {
        "number": order.pk,
        "total": order.total_price,
        "status": order.get_status_display(),
    }

    return send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        fail_silently=True,
    )
