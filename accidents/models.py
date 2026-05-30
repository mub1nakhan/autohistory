import uuid
from django.db import models
from vehicles.models import Vehicle
from django.contrib.auth import get_user_model

User = get_user_model()


class AccidentSeverity(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"


class Accident(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="accidents", db_index=True)
    severity = models.CharField(max_length=10, choices=AccidentSeverity.choices, db_index=True)
    description = models.TextField(blank=True)
    damage_parts = models.JSONField(default=list)
    accident_date = models.DateField(db_index=True)
    location = models.CharField(max_length=300, blank=True)
    mileage_at_accident = models.PositiveIntegerField(null=True, blank=True)
    report_number = models.CharField(max_length=100, blank=True)
    photos = models.JSONField(default=list, blank=True)
    verified = models.BooleanField(default=False, db_index=True)
    verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="verified_accidents"
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_accidents"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accidents"
        ordering = ["-accident_date"]
        indexes = [
            models.Index(fields=["vehicle", "-accident_date"]),
            models.Index(fields=["severity"]),
            models.Index(fields=["verified"]),
        ]

    def __str__(self):
        return f"{self.vehicle} - {self.severity} ({self.accident_date})"