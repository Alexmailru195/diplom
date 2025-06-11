# users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import User


class RegisterForm(UserCreationForm):
    """
    Форма регистрации пользователя
    """
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'Email'})
    )
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={'placeholder': 'Имя пользователя'})
    )
    first_name = forms.CharField(
        label='Имя',
        widget=forms.TextInput(attrs={'placeholder': 'Имя'}),
        required=False
    )
    last_name = forms.CharField(
        label='Фамилия',
        widget=forms.TextInput(attrs={'placeholder': 'Фамилия'}),
        required=False
    )
    phone = forms.CharField(
        label='Телефон',
        widget=forms.TextInput(attrs={'placeholder': '+7 (999) 999-99-99'}),
        required=False
    )
    password1 = forms.CharField(
        label='Пароль',
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'})
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'placeholder': 'Повторите пароль'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    """
    Форма входа пользователя
    """
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={'placeholder': 'Имя пользователя'})
    )
    password = forms.CharField(
        label='Пароль',
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль'})
    )

    class Meta:
        model = User
        fields = ('username', 'password')


class ProfileForm(forms.ModelForm):
    """
    Форма редактирования профиля
    """
    username = forms.CharField(disabled=True, label='Имя пользователя')
    email = forms.EmailField(label='Email', disabled=True)
    avatar = forms.ImageField(label='Аватар', required=False)

    first_name = forms.CharField(label='Имя', required=False)
    last_name = forms.CharField(label='Фамилия', required=False)
    phone = forms.CharField(label='Телефон', required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'avatar']


class ChangePasswordForm(forms.Form):
    """
    Форма смены пароля
    """
    old_password = forms.CharField(
        label='Старый пароль',
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Старый пароль'})
    )
    new_password1 = forms.CharField(
        label='Новый пароль',
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Новый пароль'})
    )
    new_password2 = forms.CharField(
        label='Подтвердите новый пароль',
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Подтвердите пароль'})
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self, *args, **kwargs):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Старый пароль неверен")
        return old_password

    def clean(self):
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("Пароли не совпадают")

        return self.cleaned_data

    def save(self, commit=True):
        user = self.user
        user.set_password(self.cleaned_data['new_password1'])
        if commit:
            user.save()
        return user