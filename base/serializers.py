"""Vehicles serializers."""

from rest_framework import serializers

from apps.risk_engine.models import RiskScore

from .models import Vehicle, VehicleOwnershipHistory


class VehicleOwnershipHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleOwnershipHistory
        fields = [
            "id", "owner_name", "acquired_at", "released_at",
            "transfer_mileage", "notes", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class VehicleListSerializer(serializers.ModelSerializer):
    risk_score = serializers.SerializerMethodField()
    display_name = serializers.ReadOnlyField()

    class Meta:
        model = Vehicle
        fields = [
            "id", "vin_code", "plate_number", "display_name",
            "brand", "model", "year", "color", "fuel_type",
            "mileage", "status", "risk_score", "created_at",
        ]

    def get_risk_score(self, obj):
        # Prefetched via select_related
        try:
            return obj.risk_score.risk_score
        except Exception:
            return None


class VehicleDetailSerializer(serializers.ModelSerializer):
    display_name = serializers.ReadOnlyField()
    ownership_history = VehicleOwnershipHistorySerializer(many=True, read_only=True)
    risk_score_data = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = [
            "id", "vin_code", "plate_number", "display_name",
            "brand", "model", "year", "color", "fuel_type",
            "transmission", "engine_volume", "mileage", "status",
            "ownership_count", "notes", "ownership_history",
            "risk_score_data", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_risk_score_data(self, obj):
        try:
            rs = obj.risk_score
            return {
                "score": rs.risk_score,
                "last_calculated_at": rs.last_calculated_at,
            }
        except Exception:
            return None


class VehicleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            "vin_code", "plate_number", "brand", "model", "year",
            "color", "fuel_type", "transmission", "engine_volume",
            "mileage", "status", "ownership_count", "notes",
        ]

    def validate_vin_code(self, value):
        value = value.upper().strip()
        if len(value) != 17:
            raise serializers.ValidationError("VIN must be exactly 17 characters.")
        if not value.isalnum():
            raise serializers.ValidationError("VIN must contain only alphanumeric characters.")
        # VIN cannot contain I, O, Q
        if any(c in value for c in "IOQ"):
            raise serializers.ValidationError("VIN cannot contain characters I, O, or Q.")
        return value

    def validate_year(self, value):
        from django.utils import timezone
        current_year = timezone.now().year
        if value < 1886 or value > current_year + 1:
            raise serializers.ValidationError(f"Year must be between 1886 and {current_year + 1}.")
        return value


class VehicleOwnershipTransferSerializer(serializers.Serializer):
    new_owner_name = serializers.CharField(max_length=200)
    acquired_at = serializers.DateField()
    transfer_mileage = serializers.IntegerField(min_value=0, required=False)
    notes = serializers.CharField(required=False, allow_blank=True)