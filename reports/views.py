from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import Report
from .serializers import ReportSerializer


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.select_related("vehicle").all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["vehicle", "report_type"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.full_name)