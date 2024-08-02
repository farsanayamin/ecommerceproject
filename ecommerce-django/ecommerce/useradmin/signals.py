# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from orders.models import Order

order_shipped_signal = Signal()

@receiver(order_shipped_signal)
def order_shipped(sender, instance, request, **kwargs):
    if instance.status == 'Shipped':
        email = instance.email
        mail_subject = 'Order Shipped'
        message = render_to_string('orders/shipped_mail.html', {'order': instance})
        to_email = email
        send_mail = EmailMessage(mail_subject, message, to=[to_email])
        send_mail.send()

        # Set the status to 'On the Way'
        instance.status = 'On the Way'
        instance.save()

    elif instance.status == 'On the Way':
        # Set the status to 'Delivered'
        instance.status = 'Delivered'
        instance.save()
