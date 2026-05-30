from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from users.permissions import IsAdmin
from .models import AnalyticsSnapshot
from .serializers import AnalyticsSnapshotSerializer
from vehicles.models import Vehicle
from accidents.models import Accident
from service_records.models import ServiceRecord
from inspections.models import Inspection


class AnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AnalyticsSnapshot.objects.all()
    serializer_class = AnalyticsSnapshotSerializer
    permission_classes = [IsAdmin]

    @action(detail=False, methods=["get"], url_path="overview")
    def overview(self, request):
        data = {
            "total_vehicles": Vehicle.objects.count(),
            "total_accidents": Accident.objects.count(),
            "total_service_records": ServiceRecord.objects.count(),
            "total_inspections": Inspection.objects.count(),
            "verified_accidents": Accident.objects.filter(verified=True).count(),
            "high_severity_accidents": Accident.objects.filter(severity="high").count(),
        }
        return Response(data)