# products/apps.py

from django.apps import AppConfig


class ProductsConfig(AppConfig):
    """
    Конфигурационный класс приложения 'products'.
    Определяет имя приложения, его отображаемое название в административной панели
    и тип поля по умолчанию для автоматически генерируемых первичных ключей.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'
    verbose_name = "Товары и каталог"
