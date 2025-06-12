# users/decorators.py

from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test


def superuser_or_admin_or_moderator(user):
    return user.is_superuser or user.is_staff or user.groups.filter(name='Модераторы').exists()


def permission_required(view_func):
    """
    Декоратор, который позволяет только суперпользователю, админу или модератору
    открывать страницу.
    """
    decorator = user_passes_test(superuser_or_admin_or_moderator)
    return decorator(view_func)
