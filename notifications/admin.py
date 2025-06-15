# notifications/admin.py

from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'read', 'created_at')
    list_filter = ('read', 'created_at')
    search_fields = ('user__username', 'message')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Получатель', {
            'fields': ('user',)
        }),
        ('Сообщение', {
            'fields': ('title', 'message')
        }),
        ('Статус', {
            'fields': ('read', 'created_at')
        }),
    )
    ordering = ('-created_at',)
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, queryset):
        queryset.update(read=True)
    mark_as_read.short_description = "Отметить как прочитанные"

    def mark_as_unread(self, queryset):
        queryset.update(read=False)
    mark_as_unread.short_description = "Отметить как непрочитанные"