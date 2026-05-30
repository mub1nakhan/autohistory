from .models import Inspection

class InspectionRepository:
    @staticmethod
    def get_by_id(inspection_id):
        return Inspection.objects.filter(id=inspection_id).first()

    @staticmethod
    def filter(**kwargs):
        return Inspection.objects.filter(**kwargs)

    @staticmethod
    def all():
        return Inspection.objects.all()