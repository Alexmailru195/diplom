from rest_framework import viewsets
from .models import PointOfSale
from .serializers import PointOfSaleSerializer


class PointOfSaleViewSet(viewsets.ModelViewSet):
    queryset = PointOfSale.objects.all()
    serializer_class = PointOfSaleSerializer
