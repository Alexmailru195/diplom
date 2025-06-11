from rest_framework import viewsets
from .models import Inventory
from .serializers import InventorySerializer


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.select_related('warehouse', 'product').all()
    serializer_class = InventorySerializer
