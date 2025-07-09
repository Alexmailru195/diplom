# delivery/models.py

from django.db import models


class DeliveryZone(models.Model):
    name = models.CharField(max_length=100)
    price_per_km = models.DecimalField(max_digits=6, decimal_places=2)
    base_price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name
