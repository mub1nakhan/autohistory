from .models import AuditLog

class AuditLogRepository:
    @staticmethod
    def get_by_id(log_id):
        return AuditLog.objects.filter(id=log_id).first()

    @staticmethod
    def filter(**kwargs):
        return AuditLog.objects.filter(**kwargs)

    @staticmethod
    def all():
        return AuditLog.objects.all()