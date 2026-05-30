from .models import AuditLog

class AuditLogService:
    @staticmethod
    def log_action(user, action, object_type, object_id, changes=None, ip_address=None, device_info=None):
        return AuditLog.objects.create(
            user=user,
            action=action,
            object_type=object_type,
            object_id=object_id,
            changes=changes,
            ip_address=ip_address,
            device_info=device_info
        )