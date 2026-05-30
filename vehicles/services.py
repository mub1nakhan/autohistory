from .models import Vehicle

class VehicleService:
    @staticmethod
    def create_vehicle(data):
        return Vehicle.objects.create(**data)

    @staticmethod
    def update_vehicle(vehicle, data):
        for attr, value in data.items():
            setattr(vehicle, attr, value)
        vehicle.save()
        return vehicle

    @staticmethod
    def delete_vehicle(vehicle):
        vehicle.delete()