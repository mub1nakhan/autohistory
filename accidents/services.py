from .models import Accident

class AccidentService:
    @staticmethod
    def create_accident(data):
        return Accident.objects.create(**data)

    @staticmethod
    def update_accident(accident, data):
        for attr, value in data.items():
            setattr(accident, attr, value)
        accident.save()
        return accident

    @staticmethod
    def delete_accident(accident):
        accident.delete()