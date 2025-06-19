# users/admin.py

from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Персональная информация', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Права и роль', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Даты', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role')
        }),
    )
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if obj is None:  # При создании
            form.base_fields['role'].required = True

        return form