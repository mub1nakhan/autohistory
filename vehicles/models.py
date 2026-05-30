import uuid
from django.db import models

class Vehicle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vin_code = models.CharField(max_length=32, unique=True)
    plate_number = models.CharField(max_length=16, unique=True)
    brand = models.CharField(max_length=64)
    model = models.CharField(max_length=64)
    year = models.PositiveIntegerField()
    color = models.CharField(max_length=32)
    fuel_type = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["vin_code"]),
            models.Index(fields=["plate_number"]),
            models.Index(fields=["brand", "model", "year"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.brand} {self.model} ({self.plate_number})"