from vehicles.models import Vehicle
from accidents.models import Accident
from service_records.models import ServiceRecord
from inspections.models import Inspection
from reports.models import Report
from risk_engine.models import RiskScore
from .forms import VehicleForm


def global_stats(request):
    try:
        stats = {
            "vehicles": Vehicle.objects.count(),
            "accidents": Accident.objects.count(),
            "service_records": ServiceRecord.objects.count(),
            "inspections": Inspection.objects.count(),
            "reports": Report.objects.count(),
            "risk_scores": RiskScore.objects.count(),
        }
        context = {"stats": stats}
        # provide a quick vehicle form for authenticated users (used by the modal)
        if request.user and request.user.is_authenticated:
            context["quick_vehicle_form"] = VehicleForm()
        return context
    except Exception:
        # If migrations not applied or DB unavailable, fail gracefully
        return {
            "stats": {"vehicles": 0, "accidents": 0, "service_records": 0, "inspections": 0, "reports": 0, "risk_scores": 0},
        }
