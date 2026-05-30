from .models import Report

class ReportRepository:
    @staticmethod
    def get_by_id(report_id):
        return Report.objects.filter(id=report_id).first()

    @staticmethod
    def filter(**kwargs):
        return Report.objects.filter(**kwargs)

    @staticmethod
    def all():
        return Report.objects.all()