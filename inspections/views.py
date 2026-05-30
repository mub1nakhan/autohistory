from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from users.permissions import CanAddInspection
from .models import Inspection
from .serializers import InspectionSerializer


class InspectionViewSet(viewsets.ModelViewSet):
    queryset = Inspection.objects.select_related("vehicle", "inspector").all()
    serializer_class = InspectionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["vehicle", "result"]
    search_fields = ["inspector_name", "notes"]
    ordering_fields = ["inspection_date", "rating", "created_at"]
    ordering = ["-inspection_date"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [CanAddInspection()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(inspector=user, inspector_name=serializer.validated_data.get("inspector_name") or user.full_name)