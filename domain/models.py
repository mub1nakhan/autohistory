"""Service records models — maintenance and repair history."""

import uuid

from django.contrib.auth import get_user_model
from django.db import models

from apps.vehicles.models import Vehicle

User = get_user_model()


class ServiceType(models.TextChoices):
    OIL_CHANGE = "oil_change", "Oil Change"
    TIRE_CHANGE = "tire_change", "Tire Change"
    BRAKE_SERVICE = "brake_service", "Brake Service"
    DIAGNOSTIC = "diagnostic", "Diagnostic"
    REPAIR = "repair", "Repair"
    TECHNICAL_INSPECTION = "technical_inspection", "Technical Inspection"
    BODY_WORK = "body_work", "Body Work"
    ELECTRICAL = "electrical", "Electrical"
    TRANSMISSION = "transmission", "Transmission"
    ENGINE = "engine", "Engine Work"
    COOLING = "cooling", "Cooling System"
    OTHER = "other", "Other"


class ServiceRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="service_records", db_index=True)

    service_type = models.CharField(max_length=30, choices=ServiceType.choices, db_index=True)
    description = models.TextField()
    mileage = models.PositiveIntegerField(help_text="Vehicle mileage at time of service (km)")
    service_date = models.DateField(db_index=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="USD")

    service_center_name = models.CharField(max_length=200, blank=True)
    technician_name = models.CharField(max_length=200, blank=True)

    # Parts replaced
    parts_replaced = models.JSONField(default=list, blank=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_service_records",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "service_records"
        ordering = ["-service_date"]
        indexes = [
            models.Index(fields=["vehicle", "-service_date"]),
            models.Index(fields=["service_type"]),
            models.Index(fields=["service_date"]),
        ]

    def __str__(self):
        return f"{self.vehicle.vin_code} - {self.service_type} ({self.service_date})"