# notifications/views.py
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags
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


def send_message(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message_text = request.POST.get('message')

        if not all([name, email, message_text]):
            messages.error(request, "Пожалуйста, заполните все поля.")
            return redirect('home')

        html_message = render_to_string('notifications/email_template.html', {
            'name': name,
            'email': email,
            'message': message_text
        })
        plain_message = strip_tags(html_message)

        try:
            send_mail(
                subject=f"Новое сообщение от {name}",
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_RECEIVER],
                html_message=html_message,
                fail_silently=False
            )
            messages.success(request, "Ваше сообщение было отправлено!")
        except Exception as e:
            messages.error(request, f"Ошибка при отправке сообщения: {e}")

        return redirect('home')

    return redirect('home')
