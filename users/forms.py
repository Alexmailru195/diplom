# users/forms.py

import re

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.core.exceptions import ValidationError

from .models import User


class RegisterForm(UserCreationForm):
    """
    Форма регистрации пользователя.
    Позволяет заполнить поля: логин, email, имя, фамилия и телефон.
    Выполняет проверку на уникальность email и сложность пароля.
    """

    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'Email'}),
        required=True
    )
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={'placeholder': 'Логин'}),
        required=True
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
        required=True
    )

    def clean_email(self):
        """
        Проверяет, не используется ли email уже другим пользователем.

        Raises:
            ValidationError: Если email уже существует.

        Returns:
            str: Валидированный email.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Этот email уже зарегистрирован.")
        return email

    def clean_password1(self):
        """
        Проверяет сложность пароля. Пароль должен быть:
        - Не короче 8 символов
        - Содержать хотя бы одну цифру
        - Содержать хотя бы одну строчную букву

        Raises:
            ValidationError: Если пароль не соответствует требованиям.

        Returns:
            str: Валидированный пароль.
        """
        password1 = self.cleaned_data.get('password1')
        if not password1:
            return password1

        # Проверка длины
        if len(password1) < 8:
            raise forms.ValidationError("Пароль слишком короткий. Минимум 8 символов.")

        # Проверка на наличие цифр
        if not any(char.isdigit() for char in password1):
            raise forms.ValidationError("Пароль должен содержать хотя бы одну цифру.")

        # Проверка на наличие строчных букв
        if not any(char.islower() for char in password1):
            raise forms.ValidationError("Пароль должен содержать хотя бы одну строчную букву.")

        return password1

    def clean_password2(self):
        """
        Проверяет совпадение двух введённых паролей.

        Raises:
            ValidationError: Если пароли не совпадают.

        Returns:
            str: Второй пароль.
        """
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают.")
        return password2

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    """
    Форма для входа пользователя.
    Позволяет ввести имя пользователя и пароль.
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


class ProfileForm(forms.ModelForm):
    """
    Форма редактирования профиля пользователя.
    Позволяет изменять имя, фамилию и телефон.
    Email и логин отображаются, но не редактируются.
    """

    username = forms.CharField(disabled=True, label='Имя пользователя')
    email = forms.EmailField(label='Email', disabled=True)
    first_name = forms.CharField(label='Имя', required=False)
    last_name = forms.CharField(label='Фамилия', required=False)
    phone = forms.CharField(label='Телефон', required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone']


class ChangePasswordForm(forms.Form):
    """
    Форма смены пароля.
    Позволяет ввести старый и новый пароль, а также подтвердить новый.
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

    def clean_old_password(self):
        """
        Проверяет правильность старого пароля.

        Raises:
            ValidationError: Если старый пароль неверен.

        Returns:
            str: Старый пароль.
        """
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Старый пароль неверен")
        return old_password

    def clean_new_password2(self):
        """
        Проверяет совпадение новых паролей.

        Raises:
            ValidationError: Если пароли не совпадают.

        Returns:
            str: Новый подтверждённый пароль.
        """
        new_password1 = self.cleaned_data.get('new_password1')
        new_password2 = self.cleaned_data.get('new_password2')

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("Пароли не совпадают")

        return new_password2

    def save(self, commit=True):
        """
        Сохраняет новый пароль для пользователя.

        Args:
            commit (bool): Если True — сохраняет изменения в БД.

        Returns:
            User: Обновлённый объект пользователя.
        """
        user = self.user
        user.set_password(self.cleaned_data['new_password1'])
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    """
    Форма для обновления данных профиля.
    Позволяет изменять имя, фамилию и телефон.
    """

    first_name = forms.CharField(label="Имя", required=False)
    last_name = forms.CharField(label="Фамилия", required=False)
    phone = forms.CharField(label="Телефон", required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone']

    def clean_email(self):
        """
        Проверяет формат email при обновлении профиля.

        Raises:
            ValidationError: Если email некорректного формата.

        Returns:
            str: Валидированный email.
        """
        email = self.cleaned_data.get('email')
        if not re.match(r'^[\w.-]+@[\w.-]+\.\w+$', email):
            raise forms.ValidationError("Email должен быть в корректном формате")
        return email

    def clean_phone(self):
        """
        Проверяет и форматирует номер телефона.
        Номер должен быть российским (+7 ...) и содержать 10 или 11 цифр.

        Returns:
            str: Отформатированный номер телефона.
        """
        phone = self.cleaned_data.get('phone')
        if not phone:
            return phone

        # Удаляем всё, кроме цифр
        digits = ''.join(filter(str.isdigit, phone))

        # Проверяем длину — должно быть 10 или 11 цифр
        if len(digits) < 10:
            raise forms.ValidationError("Неверная длина номера. Введите минимум 10 цифр.")
        if len(digits) > 11:
            raise forms.ValidationError("Слишком длинный номер телефона. Введите максимум 11 цифр.")

        # Если длина 10 и первая цифра — 8 → меняем на 7
        if len(digits) == 10 and digits[0] == '8':
            digits = '7' + digits[1:]

        # Если длина 11 и первая цифра не 7 → ошибка
        if len(digits) == 11 and digits[0] != '7':
            raise forms.ValidationError("Номер должен быть российским (+7 ...)")

        # Форматируем телефон как +7 XXX XXX-XX-XX
        formatted_phone = f"+7 {digits[1:4]} {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
        return formatted_phone


class CustomUserChangeForm(UserChangeForm):
    """
    Кастомная форма изменения данных пользователя.
    Используется в административной панели Django.
    """

    def clean_email(self):
        """
        Проверяет формат email.

        Raises:
            ValidationError: Если email некорректного формата.

        Returns:
            str: Валидированный email.
        """
        email = self.cleaned_data.get('email')
        if not re.match(r'^[\w.-]+@[\w.-]+\.\w+$', email):
            raise forms.ValidationError("Email должен быть в корректном формате")
        return email

    def clean_phone(self):
        """
        Проверяет и форматирует номер телефона.
        Номер должен быть российским (+7 ...) и содержать 10 или 11 цифр.

        Returns:
            str: Отформатированный номер телефона.
        """
        phone = self.cleaned_data.get('phone')
        if not phone:
            return phone

        # Удаляем всё, кроме цифр
        digits = ''.join(filter(str.isdigit, phone))

        # Проверяем длину — должно быть 10 или 11 цифр
        if len(digits) < 10:
            raise forms.ValidationError("Неверная длина номера. Введите минимум 10 цифр.")
        if len(digits) > 11:
            raise forms.ValidationError("Слишком длинный номер телефона. Введите максимум 11 цифр.")

        # Если длина 10 и первая цифра — 8 → меняем на 7
        if len(digits) == 10 and digits[0] == '8':
            digits = '7' + digits[1:]

        # Если длина 11 и первая цифра не 7 → ошибка
        if len(digits) == 11 and digits[0] != '7':
            raise forms.ValidationError("Номер должен быть российским (+7 ...)")

        # Форматируем телефон как +7 XXX XXX-XX-XX
        formatted_phone = f"+7 {digits[1:4]} {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
        return formatted_phone
