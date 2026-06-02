from django.core.exceptions import ObjectDoesNotExist

from .models import Vehicle, VehicleOwnershipHistory


class VehicleService:
    @staticmethod
    def create_vehicle(data, registered_by=None):
        data["registered_by"] = registered_by
        return Vehicle.objects.create(**data)

    @staticmethod
    def get_vehicle_by_vin(vin_code):
        return Vehicle.objects.filter(vin_code=vin_code).first()

    @staticmethod
    def update_vehicle(vehicle, data):
        for attr, value in data.items():
            setattr(vehicle, attr, value)
        vehicle.save()
        return vehicle

    @staticmethod
    def delete_vehicle(vehicle):
        vehicle.delete()

    @staticmethod
    def transfer_ownership(vehicle, transfer_data, performed_by=None):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        # Close current ownership
        VehicleOwnershipHistory.objects.filter(
            vehicle=vehicle, released_at__isnull=True
        ).update(released_at=transfer_data.get("acquired_at"))
        # New owner user
        new_owner = None
        new_owner_id = transfer_data.get("new_owner_id")
        if new_owner_id:
            try:
                new_owner = User.objects.get(id=new_owner_id)
            except User.DoesNotExist:
                pass
        history = VehicleOwnershipHistory.objects.create(
            vehicle=vehicle,
            owner=new_owner,
            owner_name=transfer_data.get("new_owner_name", ""),
            acquired_at=transfer_data["acquired_at"],
            transfer_mileage=transfer_data.get("transfer_mileage"),
            notes=transfer_data.get("notes", ""),
        )
        vehicle.owner = new_owner
        vehicle.ownership_count += 1
        vehicle.save(update_fields=["owner", "ownership_count", "updated_at"])
        return history

    @staticmethod
    def get_vehicle_summary(vehicle):
        accidents = vehicle.accidents.all()
        service_records = vehicle.service_records.all()
        inspections = vehicle.inspections.all()
        try:
            risk = vehicle.risk_score
        except ObjectDoesNotExist:
            risk = None
        return {
            "vehicle_id": str(vehicle.id),
            "display_name": vehicle.display_name,
            "vin_code": vehicle.vin_code,
            "plate_number": vehicle.plate_number,
            "status": vehicle.status,
            "mileage": vehicle.mileage,
            "accident_count": accidents.count(),
            "service_record_count": service_records.count(),
            "inspection_count": inspections.count(),
            "risk_score": risk.risk_score if risk else None,
            "ownership_count": vehicle.ownership_count,
        }
