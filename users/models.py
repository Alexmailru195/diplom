# users/models.py
import re

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Расширенная модель пользователя
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

    def __str__(self):
        return self.username

    def clean(self):
        super().clean()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['-date_joined']