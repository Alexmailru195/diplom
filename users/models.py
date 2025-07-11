# users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from pos.models import Point


class User(AbstractUser):
    """
    Расширенная модель пользователя.
    Наследует стандартную модель AbstractUser и добавляет поля: роль, телефон, email, дата регистрации,
    а также связь с пунктами выдачи (points).
    """

    ROLE_CHOICES = (
        ('customer', 'Покупатель'),
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
    )

    role = models.CharField(
        _('Роль'),
        max_length=20,
        choices=ROLE_CHOICES,
        default='customer'
    )

    phone = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(_('Дата регистрации'), auto_now_add=True)
    last_login = models.DateTimeField(_('Последний вход'), auto_now=True)
    points = models.ManyToManyField(Point, related_name='managers', blank=True)

    def __str__(self):
        return self.username

    def clean(self):
        super().clean()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['-date_joined']
