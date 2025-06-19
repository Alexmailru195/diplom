# users/decorators.py

from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test


def superuser_or_admin_or_moderator(user):
    return user.is_superuser or user.is_staff or user.groups.filter(name='Модераторы').exists()


def permission_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.path.startswith('/admin/') and not request.user.is_superuser:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Доступ запрещён")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
