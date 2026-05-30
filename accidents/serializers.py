from rest_framework import serializers
from .models import Accident


class AccidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accident
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "verified_at"]

    def validate_accident_date(self, value):
        from django.utils.timezone import now
        if value > now().date():
            raise serializers.ValidationError("Accident date cannot be in the future.")
        return value