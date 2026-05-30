"""Accidents models — accident records for vehicles."""

import uuid

from django.contrib.auth import get_user_model
from django.db import models

from apps.vehicles.models import Vehicle

User = get_user_model()


class AccidentSeverity(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"


class Accident(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="accidents", db_index=True)

    severity = models.CharField(max_length=10, choices=AccidentSeverity.choices, db_index=True)
    description = models.TextField()
    damage_parts = models.JSONField(
        default=list,
        help_text='List of damaged parts e.g. ["front_bumper", "hood", "left_door"]',
    )
    accident_date = models.DateField(db_index=True)
    location = models.CharField(max_length=300, blank=True)
    mileage_at_accident = models.PositiveIntegerField(null=True, blank=True)

    # Verification
    verified = models.BooleanField(default=False, db_index=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_accidents",
    )
    verified_at = models.DateTimeField(null=True, blank=True)

    # External reference (e.g. police report number)
    report_number = models.CharField(max_length=100, blank=True)

    # Created by
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_accidents",
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
        return f"{self.vehicle.vin_code} - {self.severity} accident ({self.accident_date})"


class AccidentPhoto(models.Model):
    """Photos attached to accident records."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    accident = models.ForeignKey(Accident, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="accidents/%Y/%m/")
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accident_photos"

    def __str__(self):
        return f"Photo for accident {self.accident_id}"