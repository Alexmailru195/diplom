# inventory/apps.py

from django.apps import AppConfig


class InventoryConfig(AppConfig):
    """
    Конфигурационный класс для приложения 'inventory'.
    Определяет имя приложения, наименование в административной панели и тип по умолчанию для автоматических полей.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'
    verbose_name = "Инвентарь и остатки"
