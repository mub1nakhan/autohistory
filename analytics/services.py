from .models import AnalyticsSnapshot

class AnalyticsService:
    @staticmethod
    def create_snapshot(data):
        return AnalyticsSnapshot.objects.create(data=data)

    @staticmethod
    def get_latest_snapshot():
        return AnalyticsSnapshot.objects.order_by('-snapshot_date').first()