"""Email helpers for order notifications."""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import gettext as _

from orders.constants import DEMO_ACTIVATION_KEY
from orders.models import Order


logger = logging.getLogger(__name__)


def _send_order_email(
    *,
    order: Order,
    notification_type: str,
    subject: str,
    message: str,
    recipient_list: list[str],
) -> int:
    """Send an order email and log delivery failures without breaking checkout."""
    try:
        return send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            "Order email delivery failed.",
            extra={
                "order_id": order.pk,
                "notification_type": notification_type,
            },
        )
        return 0


def send_order_confirmation_email(order: Order) -> int:
    """Send the demo activation key to the customer."""
    subject = _("Підтвердження замовлення №%(number)s") % {
        "number": order.pk,
    }
    message = "\n".join(
        (
            _("Дякуємо за замовлення в GameVault."),
            "",
            _("Номер замовлення: %(number)s") % {"number": order.pk},
            _("Сума: ₴%(total)s") % {"total": order.total_price},
            _("Статус: %(status)s")
            % {"status": order.digital_status_display},
            "",
            f"{_('Ключ активації')}: {DEMO_ACTIVATION_KEY}",
            _(
                "Ключ також доступний в історії замовлень. "
                "Фізична доставка не потрібна."
            ),
        )
    )

    return _send_order_email(
        order=order,
        notification_type="customer_confirmation",
        subject=subject,
        message=message,
        recipient_list=[order.email],
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
        "payment_method": order.digital_payment_method_display,
    }

    return _send_order_email(
        order=order,
        notification_type="admin_notification",
        subject=subject,
        message=message,
        recipient_list=[admin_email],
    )


def send_order_notifications(order: Order) -> int:
    """Send customer confirmation and an optional administrator notification."""
    return (
        send_order_confirmation_email(order)
        + send_admin_order_notification_email(order)
    )
