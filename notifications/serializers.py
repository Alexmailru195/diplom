# notifications/serializers.py

from rest_framework import serializers

from users.models import User
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор для уведомлений
    """
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=Notification.objects.all(),
        source='user',
        write_only=True
    )

    class Meta:
        model = Notification
        fields = ['id', 'user', 'user_id', 'title', 'message', 'read', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
        extra_kwargs = {
            'title': {'required': False}
        }

    def update(self, instance, validated_data):
        # Разрешаем обновлять только статус "read"
        instance.read = validated_data.get('read', instance.read)
        instance.save()
        return instance


class NotificationCreateSerializer(serializers.Serializer):
    """
    Сериализатор для создания уведомления через API
    """
    title = serializers.CharField(max_length=255)
    message = serializers.CharField()
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def create(self, validated_data):
        return Notification.objects.create(**validated_data)