from .models import Report

class ReportService:
    @staticmethod
    def create_report(data):
        return Report.objects.create(**data)

    @staticmethod
    def update_report(report, data):
        for attr, value in data.items():
            setattr(report, attr, value)
        report.save()
        return report

    @staticmethod
    def delete_report(report):
        report.delete()