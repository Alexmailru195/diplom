# orders/forms.py

from django import forms
from .models import Order


class OrderConfirmForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'phone', 'email', 'address', 'delivery_type', 'payment_type']
        labels = {
            'name': 'Имя',
            'phone': 'Телефон',
            'email': 'Email (необязательно)',
            'address': 'Адрес доставки',
            'delivery_type': 'Способ доставки',
            'payment_type': 'Способ оплаты',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Иван Иванов'}),
            'phone': forms.TextInput(attrs={'placeholder': '+7 (999) 123-45-67'}),
            'email': forms.EmailInput(attrs={'placeholder': 'ivanov@example.com'}),
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'г. Москва, ул. Ленина, д. 1'}),
            'delivery_type': forms.Select(choices=Order.DELIVERY_CHOICES),
            'payment_type': forms.Select(choices=Order.PAYMENT_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super(OrderConfirmForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = False
        self.fields['address'].required = False