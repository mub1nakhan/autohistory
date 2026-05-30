import uuid
from django.db import models
from vehicles.models import Vehicle

class Report(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="reports")
    report_type = models.CharField(max_length=64)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=128)

    class Meta:
        indexes = [
            models.Index(fields=["vehicle", "report_type"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.vehicle} - {self.report_type} ({self.created_at})"