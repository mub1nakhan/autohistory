from .models import RiskScore

class RiskScoreRepository:
    @staticmethod
    def get_by_vehicle(vehicle):
        return RiskScore.objects.filter(vehicle=vehicle).first()

    @staticmethod
    def all():
        return RiskScore.objects.all()