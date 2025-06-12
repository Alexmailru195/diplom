# inventory/api_views.py

from rest_framework.viewsets import ModelViewSet
from .models import PointInventory
from .serializers import PointInventorySerializer


class InventoryViewSet(ModelViewSet):
    queryset = PointInventory.objects.all()
    serializer_class = PointInventorySerializer