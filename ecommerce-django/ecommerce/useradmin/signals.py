from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from orders.models import Order
from django.dispatch import Signal
from django.db import models


order_shipped_signal = Signal()

@receiver(order_shipped_signal)
def order_shipped(sender, instance, request, **kwargs):
  if instance.status == 'Shipped':
      email = instance.email
      mail_subject = 'Order Shipped'
      message = render_to_string('orders/shipped_mail.html', {
          'order': instance,
      })
      to_email = email
      send_mail = EmailMessage(mail_subject, message, to=[to_email])
      send_mail.send()
