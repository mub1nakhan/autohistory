from rest_framework import serializers
from .models import Inspection


class InspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspection
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_rating(self, value):
        if not (1 <= value <= 10):
            raise serializers.ValidationError("Rating must be between 1 and 10.")
        return value