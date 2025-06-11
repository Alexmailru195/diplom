from rest_framework import viewsets, permissions
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Пользователь видит только свои уведомления
        return Notification.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Устанавливаем текущего пользователя автоматически
        serializer.save(user=self.request.user)
