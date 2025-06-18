# users/views.py
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .forms import RegisterForm, LoginForm, ChangePasswordForm, ProfileUpdateForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('products:product_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Отправляем письмо о регистрации
            subject = "Регистрация успешна"
            html_message = render_to_string('users/email_registered.html', {
                'user': user,
                'site_url': request.build_absolute_uri('/')
            })
            plain_message = strip_tags(html_message)

            try:
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False
                )
                messages.success(request, "Вы успешно зарегистрировались! Проверьте вашу почту.")
            except Exception as e:
                messages.warning(request, "Ошибка при отправке уведомления на почту.")

            return redirect('users:login')
        else:
            messages.error(request, "Ошибка регистрации. Проверьте введённые данные.")
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {
        'form': form
    })


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


@login_required
def profile_view(request):
    """
    Отображение и редактирование профиля
    """
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Ошибка при обновлении профиля.')
            print(form.errors)
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'users/profile.html', {
        'form': form,
    })
