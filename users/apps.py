# users/apps.py

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Конфигурационный класс приложения 'users'.
    Определяет имя приложения, его отображаемое название в административной панели
    и тип поля по умолчанию для автоматически генерируемых первичных ключей.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = "Пользователи"
