import uuid
from django.db import models
from users.models import User

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    notification_type = models.CharField(max_length=32)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "is_read"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.notification_type} ({self.created_at})"