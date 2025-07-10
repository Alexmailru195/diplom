# pos/models.py

from django.conf import settings
from django.db import models
from django import forms


class Point(models.Model):
    """
    Модель для представления пункта выдачи (точки продаж).
    Содержит информацию о названии, адресе, графика работы, координатах,
    телефоне, статусах активности и возможности самовывоза.
    """

    name = models.CharField("Название точки", max_length=100)
    address = models.TextField("Адрес")
    work_schedule = models.CharField(max_length=500, default="")
    latitude = models.FloatField(null=True, blank=True)
    phone = models.CharField("Телефон", max_length=20, blank=True, null=True)
    is_active = models.BooleanField("Активна", default=True)
    is_warehouse = models.BooleanField("Это склад", default=False)
    is_pickup = models.BooleanField("Можно забрать", default=True)

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_points'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Пункт выдачи"
        verbose_name_plural = "Пункты выдачи"


class PointForm(forms.ModelForm):
    """
    Форма для создания или редактирования модели Point.
    Включает поля: название, адрес, телефон и статус активности.
    """

    class Meta:
        model = Point
        fields = ['name', 'address', 'phone', 'is_active']
