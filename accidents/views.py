from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema

from users.permissions import IsAdmin, CanAddAccident
from .models import Accident
from .serializers import AccidentSerializer


class AccidentViewSet(viewsets.ModelViewSet):
    queryset = Accident.objects.select_related("vehicle", "created_by", "verified_by").all()
    serializer_class = AccidentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["vehicle", "severity", "verified"]
    search_fields = ["description", "location", "report_number"]
    ordering_fields = ["accident_date", "created_at", "severity"]
    ordering = ["-accident_date"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [CanAddAccident()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @extend_schema(tags=["accidents"], summary="Verify an accident report")
    @action(detail=True, methods=["post"], url_path="verify")
    def verify(self, request, pk=None):
        accident = self.get_object()
        from django.utils import timezone
        accident.verified = True
        accident.verified_by = request.user
        accident.verified_at = timezone.now()
        accident.save(update_fields=["verified", "verified_by", "verified_at"])
        return Response({"message": "Accident verified.", "id": str(accident.id)})