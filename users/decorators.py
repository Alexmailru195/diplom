# users/decorators.py

def superuser_or_admin_or_moderator(user):
    """
    Проверяет, является ли пользователь суперпользователем, администратором или модератором.

    Args:
        user: Объект пользователя Django.

    Returns:
        bool: True, если пользователь имеет хотя бы одну из указанных ролей.
    """
    return user.is_superuser or user.is_staff or user.groups.filter(name='Модераторы').exists()


def permission_required(view_func):
    """
    Декоратор для ограничения доступа к административным страницам.
    Запрещает не суперпользователям доступ к URL-адресам, начинающимся на '/admin/'.

    Args:
        view_func (function): Представление, которое будет декорировано.

    Returns:
        function: Обёрнутая функция представления.
    """
    def _wrapped_view(request, *args, **kwargs):
        if request.path.startswith('/admin/') and not request.user.is_superuser:
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Доступ запрещён")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
