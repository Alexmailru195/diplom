from django import forms
from .models import Category, Product, ProductImage


class CategoryForm(forms.ModelForm):
    """
    Форма для создания и редактирования категории товара.
    Включает поле 'name' с классом Bootstrap для стилизации.
    """

    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }


class ProductForm(forms.ModelForm):
    """
    Форма для создания и редактирования товара.
    Включает поля: имя, описание, цена, категория и флаг популярности.
    Выполняет проверку цены на положительное значение.
    """

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'is_popular']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'is_popular': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_price(self):
        """
        Проверяет цену на корректность.
        Цена должна быть положительной.

        Returns:
            float: Очищенная и валидная цена.
        """
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Цена должна быть положительной")
        return price


class ProductImageForm(forms.ModelForm):
    """
    Форма для загрузки изображения товара.
    """

    class Meta:
        model = ProductImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }
