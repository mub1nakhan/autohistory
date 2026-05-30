from django.contrib import admin
from .models import Accident


@admin.register(Accident)
class AccidentAdmin(admin.ModelAdmin):
    list_display = ["vehicle", "severity", "accident_date", "verified", "location"]
    list_filter = ["severity", "verified"]
    search_fields = ["vehicle__vin_code", "description", "report_number"]
    readonly_fields = ["id", "created_at", "updated_at"]