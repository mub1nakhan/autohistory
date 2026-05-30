from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from vehicles.models import Vehicle
from risk_engine.models import RiskScore
from service_records.models import ServiceRecord
from accidents.models import Accident
from inspections.models import Inspection
from django.db.models import Avg, Count

class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_vehicles = Vehicle.objects.count()
        avg_risk_score = RiskScore.objects.aggregate(avg=Avg('risk_score'))['avg'] or 0
        top_risky_brands = (
            Vehicle.objects.values('brand')
            .annotate(avg_risk=Avg('risk_score__risk_score'))
            .order_by('-avg_risk')[:5]
        )
        accident_frequency = Accident.objects.values('vehicle').annotate(count=Count('id')).count()
        inspection_coverage = (
            Inspection.objects.values('vehicle').distinct().count() / total_vehicles * 100 if total_vehicles else 0
        )
        return Response({
            'total_vehicles': total_vehicles,
            'avg_risk_score': avg_risk_score,
            'top_risky_brands': list(top_risky_brands),
            'accident_frequency': accident_frequency,
            'inspection_coverage_rate': inspection_coverage,
        })