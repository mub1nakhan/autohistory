import uuid
from django.db import models

class AnalyticsSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    snapshot_date = models.DateField(auto_now_add=True)
    data = models.JSONField()

    class Meta:
        ordering = ["-snapshot_date"]

    def __str__(self):
        return f"Analytics Snapshot {self.snapshot_date}"