from .models import ServiceRecord

class ServiceRecordRepository:
    @staticmethod
    def get_by_id(record_id):
        return ServiceRecord.objects.filter(id=record_id).first()

    @staticmethod
    def filter(**kwargs):
        return ServiceRecord.objects.filter(**kwargs)

    @staticmethod
    def all():
        return ServiceRecord.objects.all()