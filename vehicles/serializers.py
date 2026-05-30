from rest_framework import serializers
from .models import Vehicle, VehicleOwnershipHistory


class VehicleListSerializer(serializers.ModelSerializer):
    display_name = serializers.ReadOnlyField()
    owner_name = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            "id", "vin_code", "plate_number", "display_name",
            "brand", "model", "year", "color", "fuel_type",
            "transmission", "mileage", "status", "owner_name",
            "ownership_count", "created_at",
        ]

    def get_owner_name(self, obj):
        return obj.owner.full_name if obj.owner else None


class VehicleDetailSerializer(serializers.ModelSerializer):
    display_name = serializers.ReadOnlyField()

    class Meta:
        model = Vehicle
        fields = "__all__"


class VehicleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            "vin_code", "plate_number", "brand", "model", "year",
            "color", "fuel_type", "transmission", "engine_volume",
            "mileage", "status", "owner", "notes",
        ]

    def validate_vin_code(self, value):
        if len(value) != 17:
            raise serializers.ValidationError("VIN code must be exactly 17 characters.")
        return value.upper()


class VehicleOwnershipHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleOwnershipHistory
        fields = "__all__"


class VehicleOwnershipTransferSerializer(serializers.Serializer):
    new_owner_id = serializers.UUIDField(required=False, allow_null=True)
    new_owner_name = serializers.CharField(max_length=200)
    acquired_at = serializers.DateField()
    transfer_mileage = serializers.IntegerField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)