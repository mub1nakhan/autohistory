from django.contrib import admin
from .models import Vehicle, VehicleOwnershipHistory


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ["vin_code", "plate_number", "brand", "model", "year", "status", "mileage", "owner"]
    list_filter = ["status", "fuel_type", "transmission", "year"]
    search_fields = ["vin_code", "plate_number", "brand", "model"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(VehicleOwnershipHistory)
class OwnershipHistoryAdmin(admin.ModelAdmin):
    list_display = ["vehicle", "owner_name", "acquired_at", "released_at"]
    readonly_fields = ["id", "created_at"]