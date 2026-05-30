from .models import Notification

class NotificationRepository:
    @staticmethod
    def get_by_id(notification_id):
        return Notification.objects.filter(id=notification_id).first()

    @staticmethod
    def filter(**kwargs):
        return Notification.objects.filter(**kwargs)

    @staticmethod
    def all():
        return Notification.objects.all()