from .models import ServiceRecord

class ServiceRecordService:
    @staticmethod
    def create_service_record(data):
        return ServiceRecord.objects.create(**data)

    @staticmethod
    def update_service_record(record, data):
        for attr, value in data.items():
            setattr(record, attr, value)
        record.save()
        return record

    @staticmethod
    def delete_service_record(record):
        record.delete()