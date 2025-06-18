# users/utils.py

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_order_update_email(order, user):
    """
    Отправка уведомления о любых изменениях заказа
    """
    subject = f"Обновление статуса заказа №{order.id}"
    html_message = render_to_string('orders/order_update_email.html', {
        'order': order,
        'user': user
    })
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False
    )
