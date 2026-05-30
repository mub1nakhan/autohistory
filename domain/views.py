"""Service records views."""

import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet

from apps.users.permissions import CanAddServiceRecord, IsAdmin

from .models import ServiceRecord, ServiceType
from .serializers import ServiceRecordSerializer


class ServiceRecordFilter(django_filters.FilterSet):
    vehicle = django_filters.UUIDFilter(field_name="vehicle__id")
    service_type = django_filters.ChoiceFilter(choices=ServiceType.choices)
    date_from = django_filters.DateFilter(field_name="service_date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="service_date", lookup_expr="lte")
    mileage_min = django_filters.NumberFilter(field_name="mileage", lookup_expr="gte")
    mileage_max = django_filters.NumberFilter(field_name="mileage", lookup_expr="lte")

    class Meta:
        model = ServiceRecord
        fields = ["vehicle", "service_type"]


@extend_schema_view(
    list=extend_schema(tags=["service-records"], summary="List service records"),
    retrieve=extend_schema(tags=["service-records"], summary="Get service record"),
    create=extend_schema(tags=["service-records"], summary="Add service record"),
    update=extend_schema(tags=["service-records"], summary="Update service record"),
    partial_update=extend_schema(tags=["service-records"], summary="Partial update"),
    destroy=extend_schema(tags=["service-records"], summary="Delete service record"),
)
class ServiceRecordViewSet(ModelViewSet):
    queryset = (
        ServiceRecord.objects.select_related("vehicle", "created_by")
        .order_by("-service_date")
    )
    serializer_class = ServiceRecordSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ServiceRecordFilter
    ordering_fields = ["service_date", "mileage", "cost"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [CanAddServiceRecord()]
        return super().get_permissions()

    def perform_create(self, serializer):
        record = serializer.save(created_by=self.request.user)
        # Trigger risk score recalculation
        from apps.risk_engine.tasks import calculate_vehicle_risk_score
        calculate_vehicle_risk_score.delay(str(record.vehicle.id))