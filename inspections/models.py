import uuid
from django.db import models
from vehicles.models import Vehicle
from django.contrib.auth import get_user_model

User = get_user_model()


class InspectionResult(models.TextChoices):
    PASSED = "passed", "Passed"
    FAILED = "failed", "Failed"
    CONDITIONAL = "conditional", "Conditional Pass"


class Inspection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="inspections", db_index=True)
    inspector = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="conducted_inspections"
    )
    inspector_name = models.CharField(max_length=128)
    result = models.CharField(max_length=20, choices=InspectionResult.choices, db_index=True)
    notes = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(help_text="Rating out of 10")
    inspection_date = models.DateField(db_index=True)
    next_inspection_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "inspections"    
        ordering = ["-inspection_date"]
        indexes = [
            models.Index(fields=["vehicle", "-inspection_date"]),
            models.Index(fields=["result"]),
        ]

    def __str__(self):
        return f"{self.vehicle} - {self.inspector_name} ({self.inspection_date})"