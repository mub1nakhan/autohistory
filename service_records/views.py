from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from users.permissions import IsAdminOrServiceCenter
from .models import ServiceRecord
from .serializers import ServiceRecordSerializer


class ServiceRecordViewSet(viewsets.ModelViewSet):
    queryset = ServiceRecord.objects.select_related("vehicle", "created_by").all()
    serializer_class = ServiceRecordSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["vehicle", "service_type"]
    search_fields = ["description", "service_center_name", "technician_name"]
    ordering_fields = ["service_date", "created_at", "mileage", "cost"]
    ordering = ["-service_date"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminOrServiceCenter()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)