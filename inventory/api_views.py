# inventory/api_views.py

from rest_framework.viewsets import ModelViewSet
from .models import PointInventory
from .serializers import PointInventorySerializer


class InventoryViewSet(ModelViewSet):
    """
    API-вьюсет для управления моделью PointInventory.
    Позволяет получать, создавать, обновлять и удалять записи об остатках товаров на разных точках.
    """

    queryset = PointInventory.objects.all()
    serializer_class = PointInventorySerializer
