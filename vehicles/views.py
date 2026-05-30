import logging
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users.permissions import IsAdmin
from .models import Vehicle
from .serializers import (
    VehicleListSerializer,
    VehicleDetailSerializer,
    VehicleCreateSerializer,
    VehicleOwnershipTransferSerializer,
)
from .services import VehicleService

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(tags=["vehicles"], summary="List vehicles"),
    retrieve=extend_schema(tags=["vehicles"], summary="Get vehicle details"),
    create=extend_schema(tags=["vehicles"], summary="Register new vehicle"),
    update=extend_schema(tags=["vehicles"], summary="Update vehicle"),
    partial_update=extend_schema(tags=["vehicles"], summary="Partial update vehicle"),
    destroy=extend_schema(tags=["vehicles"], summary="Delete vehicle (admin only)"),
)
class VehicleViewSet(ModelViewSet):
    queryset = (
        Vehicle.objects.select_related("owner", "registered_by")
        .prefetch_related("ownership_history")
        .order_by("-created_at")
    )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["brand", "model", "year", "status", "fuel_type"]
    search_fields = ["vin_code", "plate_number", "brand", "model"]
    ordering_fields = ["created_at", "year", "mileage"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return VehicleCreateSerializer
        if self.action == "retrieve":
            return VehicleDetailSerializer
        return VehicleListSerializer

    def get_permissions(self):
        if self.action == "destroy":
            return [IsAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        vehicle = VehicleService.create_vehicle(
            data=serializer.validated_data,
            registered_by=self.request.user,
        )
        serializer.instance = vehicle

    @extend_schema(tags=["vehicles"], summary="Get vehicle by VIN")
    @action(detail=False, methods=["get"], url_path="vin/(?P<vin_code>[^/.]+)")
    def by_vin(self, request, vin_code=None):
        vehicle = VehicleService.get_vehicle_by_vin(vin_code)
        if not vehicle:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "Vehicle not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(VehicleDetailSerializer(vehicle).data)

    @extend_schema(tags=["vehicles"], summary="Transfer vehicle ownership")
    @action(detail=True, methods=["post"], url_path="transfer-ownership")
    def transfer_ownership(self, request, pk=None):
        vehicle = self.get_object()
        serializer = VehicleOwnershipTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        history = VehicleService.transfer_ownership(
            vehicle=vehicle,
            transfer_data=serializer.validated_data,
            performed_by=request.user,
        )
        return Response({"message": "Ownership transferred.", "history_id": str(history.id)})

    @extend_schema(tags=["vehicles"], summary="Vehicle summary statistics")
    @action(detail=True, methods=["get"], url_path="summary")
    def summary(self, request, pk=None):
        vehicle = self.get_object()
        return Response(VehicleService.get_vehicle_summary(vehicle))