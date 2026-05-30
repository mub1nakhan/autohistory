from .models import Inspection

class InspectionService:
    @staticmethod
    def create_inspection(data):
        return Inspection.objects.create(**data)

    @staticmethod
    def update_inspection(inspection, data):
        for attr, value in data.items():
            setattr(inspection, attr, value)
        inspection.save()
        return inspection

    @staticmethod
    def delete_inspection(inspection):
        inspection.delete()