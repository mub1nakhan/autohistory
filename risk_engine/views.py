from rest_framework import viewsets
from .models import RiskScore
from .serializers import RiskScoreSerializer
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

class RiskScoreViewSet(viewsets.ModelViewSet):
    queryset = RiskScore.objects.all()
    serializer_class = RiskScoreSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['vehicle', 'risk_score']