from .models import Accident

class AccidentRepository:
    @staticmethod
    def get_by_id(accident_id):
        return Accident.objects.filter(id=accident_id).first()

    @staticmethod
    def filter(**kwargs):
        return Accident.objects.filter(**kwargs)

    @staticmethod
    def all():
        return Accident.objects.all()