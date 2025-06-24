# cart/signals.py

from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from .utils import merge_guest_cart_to_user_cart


@receiver(user_logged_in)
def merge_guest_cart_on_login(sender, user, request, **kwargs):
    merge_guest_cart_to_user_cart(request)
