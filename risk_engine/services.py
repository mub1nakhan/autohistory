from .models import RiskScore
from vehicles.models import Vehicle
from accidents.models import Accident
from service_records.models import ServiceRecord
from inspections.models import Inspection
from django.utils import timezone
from django.db.models import Count, Q

class RiskEngineService:
    @staticmethod
    def calculate_risk(vehicle_id):
        vehicle = Vehicle.objects.get(id=vehicle_id)
        accidents = Accident.objects.filter(vehicle=vehicle)
        service_records = ServiceRecord.objects.filter(vehicle=vehicle)
        inspections = Inspection.objects.filter(vehicle=vehicle)
        risk = 0
        breakdown = {}
        # Accident severity
        severity_score = 0
        for acc in accidents:
            if acc.severity == 'high':
                severity_score += 15
            elif acc.severity == 'medium':
                severity_score += 10
            elif acc.severity == 'low':
                severity_score += 5
        severity_score = min(severity_score, 30)
        breakdown['accident_severity'] = severity_score
        risk += severity_score
        # Number of accidents
        num_accidents = accidents.count()
        risk += min(num_accidents * 2, 10)
        breakdown['accident_count'] = min(num_accidents * 2, 10)
        # Mileage inconsistency (placeholder, real logic needed)
        mileage_inconsistency = 0
        if service_records.count() > 1:
            mileages = list(service_records.values_list('mileage', flat=True))
            if mileages != sorted(mileages):
                mileage_inconsistency = 25
        breakdown['mileage_inconsistency'] = mileage_inconsistency
        risk += mileage_inconsistency
        # Lack of service records
        lack_service = 20 if service_records.count() == 0 else 0
        breakdown['lack_of_service_records'] = lack_service
        risk += lack_service
        # Old or missing inspections
        old_inspection = 0
        if not inspections.exists() or (timezone.now().date() - inspections.latest('inspection_date').inspection_date).days > 365:
            old_inspection = 15
        breakdown['old_or_missing_inspections'] = old_inspection
        risk += old_inspection
        # Ownership changes frequency (placeholder, real logic needed)
        ownership_changes = 0  # To be implemented
        breakdown['ownership_changes'] = ownership_changes
        risk += min(ownership_changes, 10)
        # Final risk
        risk = min(risk, 100)
        breakdown['final_risk_score'] = risk
        # Save or update
        obj, _ = RiskScore.objects.update_or_create(vehicle=vehicle, defaults={
            'risk_score': risk,
            'breakdown_json': breakdown,
            'last_calculated_at': timezone.now()
        })
        return obj