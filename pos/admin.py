from django.contrib import admin
from .models import PointOfSale


@admin.register(PointOfSale)
class PointOfSaleAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'working_hours', 'contact_phone', 'is_active')
    search_fields = ('name', 'address')
    list_filter = ('is_active',)
