"""Vehicles service layer — business logic for vehicle domain."""

import logging

from django.db import transaction

from .models import Vehicle, VehicleOwnershipHistory

logger = logging.getLogger(__name__)


class VehicleService:
    """Business logic for vehicle management."""

    @staticmethod
    @transaction.atomic
    def create_vehicle(data, registered_by):
        vehicle = Vehicle.objects.create(
            **data,
            registered_by=registered_by,
        )
        # Record initial ownership if owner_name provided
        logger.info(f"Vehicle registered: {vehicle.vin_code} by user {registered_by.id}")
        return vehicle

    @staticmethod
    @transaction.atomic
    def transfer_ownership(vehicle, transfer_data, performed_by):
        """Transfer vehicle ownership and record history."""
        from django.utils import timezone

        # Close current ownership record
        VehicleOwnershipHistory.objects.filter(
            vehicle=vehicle, released_at__isnull=True
        ).update(released_at=transfer_data.get("acquired_at"), transfer_mileage=transfer_data.get("transfer_mileage"))

        # Create new ownership record
        history = VehicleOwnershipHistory.objects.create(
            vehicle=vehicle,
            owner_name=transfer_data["new_owner_name"],
            acquired_at=transfer_data["acquired_at"],
            transfer_mileage=transfer_data.get("transfer_mileage"),
            notes=transfer_data.get("notes", ""),
        )

        # Increment ownership count
        vehicle.ownership_count += 1
        vehicle.save(update_fields=["ownership_count", "updated_at"])

        # Trigger risk score recalculation
        from apps.risk_engine.tasks import calculate_vehicle_risk_score
        calculate_vehicle_risk_score.delay(str(vehicle.id))

        logger.info(
            f"Ownership transferred for vehicle {vehicle.vin_code} "
            f"to {transfer_data['new_owner_name']} by user {performed_by.id}"
        )
        return history

    @staticmethod
    def get_vehicle_by_vin(vin_code):
        try:
            return Vehicle.objects.select_related("risk_score").get(
                vin_code=vin_code.upper().strip()
            )
        except Vehicle.DoesNotExist:
            return None

    @staticmethod
    def get_vehicle_summary(vehicle):
        """Get aggregated summary stats for a vehicle."""
        from apps.accidents.models import Accident
        from apps.inspections.models import Inspection
        from apps.service_records.models import ServiceRecord

        return {
            "accidents_count": Accident.objects.filter(vehicle=vehicle).count(),
            "service_records_count": ServiceRecord.objects.filter(vehicle=vehicle).count(),
            "inspections_count": Inspection.objects.filter(vehicle=vehicle).count(),
            "ownership_changes": vehicle.ownership_count,
        }