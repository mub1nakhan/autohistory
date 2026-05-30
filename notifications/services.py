from .models import Notification
from users.models import User
from django.core.mail import send_mail
from django.conf import settings

class NotificationService:
    @staticmethod
    def send_email(user_id, subject, message):
        user = User.objects.get(id=user_id)
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

    @staticmethod
    def create_notification(user_id, message, notification_type):
        user = User.objects.get(id=user_id)
        return Notification.objects.create(user=user, message=message, notification_type=notification_type)

    # Telegram and in-app notification logic to be added