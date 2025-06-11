# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileForm, ChangePasswordForm


def register_view(request):
    """
    Регистрация нового пользователя
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Вы успешно зарегистрировались")
            return redirect('products:product_list')
        else:
            messages.error(request, "Ошибка регистрации")
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """
    Вход пользователя
    """
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Добро пожаловать, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Неверное имя пользователя или пароль")

    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """
    Выход из аккаунта
    """
    logout(request)
    messages.info(request, "Вы вышли из аккаунта")
    return redirect('home')


@login_required
def profile_view(request):
    """
    Просмотр и редактирование профиля
    """
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлён")
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'users/profile.html', {
        'form': form,
    })


@login_required
def change_password_view(request):
    """
    Смена пароля
    """
    if request.method == 'POST':
        password_form = ChangePasswordForm(user=request.user, data=request.POST)
        if password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Пароль изменён")
            return redirect('users:profile')
    else:
        password_form = ChangePasswordForm(user=request.user)

    return render(request, 'users/change_password.html', {
        'form': password_form
    })