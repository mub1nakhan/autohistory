"""Service records serializers."""

from rest_framework import serializers

from .models import ServiceRecord


class ServiceRecordSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ServiceRecord
        fields = [
            "id", "vehicle", "service_type", "description",
            "mileage", "service_date", "cost", "currency",
            "service_center_name", "technician_name",
            "parts_replaced", "created_by", "created_by_name",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def get_created_by_name(self, obj):
        return obj.created_by.full_name if obj.created_by else None

    def validate_mileage(self, value):
        vehicle_id = self.initial_data.get("vehicle")
        if vehicle_id:
            # Get the latest service record mileage for this vehicle
            from .models import ServiceRecord as SR
            last_record = (
                SR.objects.filter(vehicle_id=vehicle_id)
                .order_by("-service_date", "-mileage")
                .first()
            )
            if last_record and value < last_record.mileage:
                raise serializers.ValidationError(
                    f"Mileage ({value} km) cannot be less than the previous record ({last_record.mileage} km). "
                    "Possible mileage rollback detected."
                )
        return value


class ServiceRecordCreateSerializer(ServiceRecordSerializer):
    class Meta(ServiceRecordSerializer.Meta):
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]