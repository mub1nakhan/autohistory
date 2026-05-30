from rest_framework import serializers
from .models import RiskScore


class RiskScoreSerializer(serializers.ModelSerializer):
    vehicle_display = serializers.SerializerMethodField()

    class Meta:
        model = RiskScore
        fields = "__all__"

    def get_vehicle_display(self, obj):
        return str(obj.vehicle)