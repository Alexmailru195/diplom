from django.db import models


class PointOfSale(models.Model):
    name = models.CharField('Название точки', max_length=255)
    address = models.TextField('Адрес')
    working_hours = models.CharField('График работы', max_length=255)
    contact_phone = models.CharField('Телефон', max_length=20, blank=True, null=True)
    is_active = models.BooleanField('Активна', default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Точка продаж'
        verbose_name_plural = 'Точки продаж'
