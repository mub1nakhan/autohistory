"""Accidents views."""

import django_filters
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.users.permissions import CanAddAccident, IsAdminOrInspector

from .models import Accident, AccidentSeverity
from .serializers import AccidentListSerializer, AccidentSerializer


class AccidentFilter(django_filters.FilterSet):
    vehicle = django_filters.UUIDFilter(field_name="vehicle__id")
    severity = django_filters.ChoiceFilter(choices=AccidentSeverity.choices)
    verified = django_filters.BooleanFilter()
    date_from = django_filters.DateFilter(field_name="accident_date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="accident_date", lookup_expr="lte")

    class Meta:
        model = Accident
        fields = ["vehicle", "severity", "verified"]


@extend_schema_view(
    list=extend_schema(tags=["accidents"], summary="List accident records"),
    retrieve=extend_schema(tags=["accidents"], summary="Get accident details"),
    create=extend_schema(tags=["accidents"], summary="Add accident record"),
    update=extend_schema(tags=["accidents"], summary="Update accident"),
    destroy=extend_schema(tags=["accidents"], summary="Delete accident"),
)
class AccidentViewSet(ModelViewSet):
    queryset = (
        Accident.objects.select_related("vehicle", "created_by", "verified_by")
        .prefetch_related("photos")
        .order_by("-accident_date")
    )
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = AccidentFilter
    ordering_fields = ["accident_date", "severity", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return AccidentListSerializer
        return AccidentSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [CanAddAccident()]
        return super().get_permissions()

    def perform_create(self, serializer):
        accident = serializer.save(created_by=self.request.user)
        # Trigger risk recalculation
        from apps.risk_engine.tasks import calculate_vehicle_risk_score
        calculate_vehicle_risk_score.delay(str(accident.vehicle.id))
        # Send notification
        from apps.notifications.tasks import notify_new_accident
        notify_new_accident.delay(str(accident.id))

    @extend_schema(tags=["accidents"], summary="Verify an accident record")
    @action(detail=True, methods=["post"], url_path="verify", permission_classes=[IsAdminOrInspector])
    def verify(self, request, pk=None):
        accident = self.get_object()
        if accident.verified:
            return Response(
                {"error": {"code": "ALREADY_VERIFIED", "message": "This accident is already verified."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        accident.verified = True
        accident.verified_by = request.user
        accident.verified_at = timezone.now()
        accident.save(update_fields=["verified", "verified_by", "verified_at", "updated_at"])
        # Recalculate risk
        from apps.risk_engine.tasks import calculate_vehicle_risk_score
        calculate_vehicle_risk_score.delay(str(accident.vehicle.id))
        return Response({"message": "Accident verified."})