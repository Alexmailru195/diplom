# pos/forms.py

from django import forms
from .models import Point


class PointForm(forms.ModelForm):
    class Meta:
        model = Point
        fields = ['name', 'address', 'phone', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(),
        }