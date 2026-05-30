"""Accidents serializers."""

from django.utils import timezone
from rest_framework import serializers

from .models import Accident, AccidentPhoto


class AccidentPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccidentPhoto
        fields = ["id", "image", "caption", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]


class AccidentSerializer(serializers.ModelSerializer):
    photos = AccidentPhotoSerializer(many=True, read_only=True)
    created_by_name = serializers.SerializerMethodField()
    verified_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Accident
        fields = [
            "id", "vehicle", "severity", "description",
            "damage_parts", "accident_date", "location",
            "mileage_at_accident", "verified", "verified_by",
            "verified_by_name", "verified_at", "report_number",
            "photos", "created_by", "created_by_name",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "verified", "verified_by", "verified_at",
            "created_by", "created_at", "updated_at",
        ]

    def get_created_by_name(self, obj):
        return obj.created_by.full_name if obj.created_by else None

    def get_verified_by_name(self, obj):
        return obj.verified_by.full_name if obj.verified_by else None


class AccidentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accident
        fields = [
            "id", "vehicle", "severity", "accident_date",
            "location", "verified", "created_at",
        ]