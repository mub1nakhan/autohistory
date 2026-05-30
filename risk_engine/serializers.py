from rest_framework import serializers
from .models import RiskScore

class RiskScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskScore
        fields = '__all__'