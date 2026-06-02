from django.contrib import admin
from .models import Vehicle, VehicleOwnershipHistory


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = [
        "vin_code",
        "plate_number",
        "brand",
        "model",
        "year",
        "status",
        "mileage",
        "price",
        "workshop_visits",
        "is_verified",
        "owner",
    ]
    list_editable = ["price", "workshop_visits", "is_verified"]
    list_filter = ["status", "fuel_type", "transmission", "year", "is_verified"]
    autocomplete_fields = ["owner", "registered_by"]
    search_fields = ["vin_code", "plate_number", "brand", "model"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("vin_code", "plate_number", "brand", "model", "year", "color", "price", "currency")} ),
        ("Technical", {"fields": ("fuel_type", "transmission", "engine_volume", "mileage", "workshop_visits")} ),
        ("Ownership", {"fields": ("owner", "registered_by", "ownership_count")} ),
        ("Status", {"fields": ("status", "is_verified", "notes")} ),
    )
    inlines = []
    actions = ["mark_verified", "mark_unverified"]

    def mark_verified(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"Marked {updated} vehicle(s) as verified.")
    mark_verified.short_description = "Mark selected vehicles as verified"

    def mark_unverified(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f"Marked {updated} vehicle(s) as unverified.")
    mark_unverified.short_description = "Mark selected vehicles as unverified"


class OwnershipInline(admin.TabularInline):
    model = VehicleOwnershipHistory
    extra = 1

# attach inline to VehicleAdmin
VehicleAdmin.inlines = [OwnershipInline]


@admin.register(VehicleOwnershipHistory)
class OwnershipHistoryAdmin(admin.ModelAdmin):
    list_display = ["vehicle", "owner_name", "acquired_at", "released_at"]
    readonly_fields = ["id", "created_at"]