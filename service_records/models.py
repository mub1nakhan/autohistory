import uuid
from django.db import models
from vehicles.models import Vehicle
from users.models import User

class ServiceRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="service_records")
    service_type = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    mileage = models.PositiveIntegerField()
    service_date = models.DateField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["vehicle", "service_date"]),
        ]
        ordering = ["-service_date"]

    def __str__(self):
        return f"{self.vehicle} - {self.service_type} ({self.service_date})"