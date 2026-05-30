from rest_framework import viewsets
from .models import Vehicle
from .serializers import VehicleSerializer
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['brand', 'model', 'year']
    search_fields = ['vin_code', 'plate_number', 'brand', 'model']
    ordering_fields = ['created_at', 'risk_score__risk_score']
    ordering = ['-created_at']