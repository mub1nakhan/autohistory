import uuid
from django.db import models
from vehicles.models import Vehicle

class RiskScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name="risk_score")
    risk_score = models.PositiveIntegerField()
    breakdown_json = models.JSONField()
    last_calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["vehicle"]),
        ]

    def __str__(self):
        return f"{self.vehicle} - {self.risk_score}"