from .models import AnalyticsSnapshot

class AnalyticsRepository:
    @staticmethod
    def get_by_id(snapshot_id):
        return AnalyticsSnapshot.objects.filter(id=snapshot_id).first()

    @staticmethod
    def all():
        return AnalyticsSnapshot.objects.all()