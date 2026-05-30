from rest_framework import viewsets
from .models import Accident
from .serializers import AccidentSerializer
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

class AccidentViewSet(viewsets.ModelViewSet):
    queryset = Accident.objects.all()
    serializer_class = AccidentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['vehicle', 'severity', 'verified', 'date']