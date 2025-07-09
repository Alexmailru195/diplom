# orders/forms.py

from django import forms

from orders.models import Order


class OrderConfirmForm(forms.Form):
    """
    Форма для подтверждения заказа.
    Включает поля для выбора типа доставки, адреса, пункта самовывоза, даты и времени получения,
    а также контактные данные клиента.
    """

    DELIVERY_CHOICES = (
        ('courier', 'Доставка'),
        ('pickup', 'Самовывоз'),
    )

    PAYMENT_CHOICES = (
        ('online', 'Онлайн'),
        ('cash', 'Наличные/безналичные при получении'),
    )

    TIME_SLOT_CHOICES = (
        ('morning', 'Утро (9:00–13:00)'),
        ('afternoon', 'День (13:00–17:00)'),
    )

    class Meta:
        model = Order
        fields = [
            'name',
            'phone',
            'email',
            'delivery_type',
            'address',
            'pickup_point',
            'delivery_date',
            'time_slot',
            'payment_type'
        ]

    delivery_type = forms.ChoiceField(
        choices=DELIVERY_CHOICES,
        label="Тип доставки",
        widget=forms.Select(attrs={'id': 'id_delivery_type'})
    )
    pickup_point = forms.IntegerField(
        required=False,
        label="Пункт самовывоза"
    )
    address = forms.CharField(
        required=False,
        label="Адрес доставки",
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'г. Москва, ул. Ленина, д. 1'})
    )
    delivery_date = forms.CharField(
        required=False,
        label="Дата доставки",
        widget=forms.TextInput(attrs={'placeholder': 'дд.мм.гггг'})
    )
    time_slot = forms.ChoiceField(
        choices=TIME_SLOT_CHOICES,
        required=False,
        label="Время доставки",
        widget=forms.Select(attrs={'id': 'id_time_slot'})
    )
    name = forms.CharField(
        max_length=100,
        label="Имя",
        widget=forms.TextInput(attrs={'placeholder': 'Иван Иванов'})
    )
    phone = forms.CharField(
        max_length=20,
        label="Телефон",
        widget=forms.TextInput(attrs={'placeholder': '+7 (999) 123-45-67'})
    )
    email = forms.EmailField(
        required=False,
        label="Email (необязательно)",
        widget=forms.EmailInput(attrs={'placeholder': 'ivanov@example.com'})
    )
    payment_type = forms.ChoiceField(choices=PAYMENT_CHOICES)

    def clean(self):
        """
        Проверяет обязательные поля формы.
        Если выбран самовывоз, пункт самовывоза должен быть указан.

        Returns:
            dict: Очищенные данные формы.
        """
        cleaned_data = super().clean()
        delivery_type = cleaned_data.get('delivery_type')
        pickup_point = cleaned_data.get('pickup_point')

        if delivery_type == 'pickup' and not pickup_point:
            self.add_error('pickup_point', "Выберите пункт самовывоза")

        return cleaned_data
