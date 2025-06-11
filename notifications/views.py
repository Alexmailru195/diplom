# notifications/views.py

from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from .models import Notification
from .serializers import NotificationSerializer, NotificationCreateSerializer


class NotificationViewSet(ViewSet):
    """
    API endpoint для управления уведомлениями пользователя.
    """

    def list(self, request):
        """
        Получить список всех уведомлений текущего пользователя
        """
        notifications = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Получить одно уведомление по ID
        """
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            serializer = NotificationSerializer(notification)
            return Response(serializer.data)
        except Notification.DoesNotExist:
            return Response({"detail": "Уведомление не найдено"}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        """
        Создать новое уведомление (для тестов или внутреннего API)
        """
        serializer = NotificationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notification = serializer.save()
        return Response(NotificationSerializer(notification).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        """
        Обновить статус уведомления (например, отметить как прочитанное)
        """
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response({"detail": "Уведомление не найдено"}, status=status.HTTP_404_NOT_FOUND)

        serializer = NotificationSerializer(notification, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        """
        Отметить одно или несколько уведомлений как прочитанные
        """
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"detail": "Не указаны ID уведомлений"}, status=status.HTTP_400_BAD_REQUEST)

        updated = Notification.objects.filter(id__in=ids, user=request.user).update(read=True)
        return Response({
            "detail": f"{updated} уведомлений отмечено как прочитанные"
        })

    @action(detail=False, methods=['post'])
    def mark_unread(self, request):
        """
        Отметить одно или несколько уведомлений как непрочитанные
        """
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"detail": "Не указаны ID уведомлений"}, status=status.HTTP_400_BAD_REQUEST)

        updated = Notification.objects.filter(id__in=ids, user=request.user).update(read=False)
        return Response({
            "detail": f"{updated} уведомлений отмечено как непрочитанные"
        })