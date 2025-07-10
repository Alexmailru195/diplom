# pos/apps.py

from django.apps import AppConfig


class PosConfig(AppConfig):
    """
    Конфигурационный класс приложения 'pos'.
    Определяет имя приложения, его отображаемое название в административной панели
    и тип поля по умолчанию для автоматически генерируемых первичных ключей.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pos'
    verbose_name = "Точки продаж (POS)"
