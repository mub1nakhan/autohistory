from .models import Vehicle

class VehicleRepository:
    @staticmethod
    def get_by_id(vehicle_id):
        return Vehicle.objects.filter(id=vehicle_id).first()

    @staticmethod
    def filter(**kwargs):
        return Vehicle.objects.filter(**kwargs)

    @staticmethod
    def all():
        return Vehicle.objects.all()