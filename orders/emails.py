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


def send_admin_order_notification_email(order: Order) -> int:
    """Notify the configured administrator about a new order."""
    admin_email = settings.ADMIN_EMAIL.strip()
    if not admin_email:
        return 0

    subject = _("Нове замовлення №%(number)s") % {"number": order.pk}
    message = _(
        "У GameVault створено нове замовлення.\n\n"
        "Номер замовлення: %(number)s\n"
        "Покупець: %(customer)s\n"
        "Електронна пошта: %(email)s\n"
        "Сума: ₴%(total)s\n"
        "Спосіб оплати: %(payment_method)s"
    ) % {
        "number": order.pk,
        "customer": f"{order.first_name} {order.last_name}".strip(),
        "email": order.email,
        "total": order.total_price,
        "payment_method": order.get_payment_method_display(),
    }

    return send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[admin_email],
        fail_silently=True,
    )


def send_order_notifications(order: Order) -> int:
    """Send customer confirmation and an optional administrator notification."""
    return (
        send_order_confirmation_email(order)
        + send_admin_order_notification_email(order)
    )
