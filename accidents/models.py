import uuid
from django.db import models
from vehicles.models import Vehicle

class Accident(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="accidents")
    severity = models.CharField(max_length=16, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')])
    description = models.TextField(blank=True)
    damage_parts = models.JSONField()
    date = models.DateField()
    photos = models.JSONField(blank=True, null=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["vehicle", "date"]),
        ]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.vehicle} - {self.severity} ({self.date})"