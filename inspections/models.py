import uuid
from django.db import models
from vehicles.models import Vehicle

class Inspection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="inspections")
    inspector_name = models.CharField(max_length=128)
    result = models.CharField(max_length=128)
    notes = models.TextField(blank=True)
    rating = models.PositiveIntegerField()
    inspection_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["vehicle", "inspection_date"]),
        ]
        ordering = ["-inspection_date"]

    def __str__(self):
        return f"{self.vehicle} - {self.inspector_name} ({self.inspection_date})"