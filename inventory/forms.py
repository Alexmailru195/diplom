# inventory/forms.py

from django import forms
from .models import StockMovement
from .models import PointInventory
from products.models import Product
from pos.models import Point


class InventoryMoveForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), label="Товар")
    from_point = forms.ModelChoiceField(queryset=Point.objects.all(), label="Из точки")
    to_point = forms.ModelChoiceField(queryset=Point.objects.all(), label="В точку")
    quantity = forms.IntegerField(min_value=1, label="Количество")

    class Meta:
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'from_point': forms.Select(attrs={'class': 'form-select'}),
            'to_point': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'})
        }


class PointInventoryForm(forms.ModelForm):
    class Meta:
        model = PointInventory
        fields = ['point', 'product', 'quantity']
        widgets = {
            'point': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
        }