# orders/forms.py

from django import forms
from pos.models import Point


class OrderConfirmForm(forms.Form):
    DELIVERY_CHOICES = (
        ('courier', 'Доставка'),
        ('pickup', 'Самовывоз'),
    )

    PAYMENT_CHOICES = (
        ('online', 'Онлайн'),
        ('cash', 'Наличные при получении'),
    )

    delivery_date = forms.DateField(
        required=False,
        label="Дата доставки",
        widget=forms.DateInput(attrs={'placeholder': 'Выберите дату', 'type': 'date'})
    )
    delivery_time = forms.TimeField(
        required=False,
        label="Время доставки",
        widget=forms.TimeInput(attrs={'placeholder': 'Выберите время', 'type': 'time'})
    )

    delivery_type = forms.ChoiceField(choices=DELIVERY_CHOICES, label="Тип доставки")
    pickup_point = forms.IntegerField(required=False, label="Пункт самовывоза")
    address = forms.CharField(required=False, label="Адрес доставки")
    delivery_date = forms.DateField(required=False, label="Дата доставки")
    delivery_time = forms.TimeField(required=False, label="Время доставки")
    name = forms.CharField(max_length=100, label="Имя")
    phone = forms.CharField(max_length=20, label="Телефон")
    email = forms.EmailField(required=False, label="Email (необязательно)")
    payment_type = forms.ChoiceField(choices=PAYMENT_CHOICES, label="Способ оплаты")

    def clean(self):
        cleaned_data = super().clean()
        delivery_type = cleaned_data.get('delivery_type')
        pickup_point = cleaned_data.get('pickup_point')

        if delivery_type == 'pickup' and not pickup_point:
            raise forms.ValidationError("Выберите пункт самовывоза")

        return cleaned_data