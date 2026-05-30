"""Vehicles filter configuration."""

import django_filters
from django.db.models import Q

from .models import FuelType, Vehicle, VehicleStatus


class VehicleFilter(django_filters.FilterSet):
    brand = django_filters.CharFilter(lookup_expr="icontains")
    model = django_filters.CharFilter(lookup_expr="icontains")
    year = django_filters.NumberFilter()
    year_min = django_filters.NumberFilter(field_name="year", lookup_expr="gte")
    year_max = django_filters.NumberFilter(field_name="year", lookup_expr="lte")
    fuel_type = django_filters.ChoiceFilter(choices=FuelType.choices)
    status = django_filters.ChoiceFilter(choices=VehicleStatus.choices)
    risk_score_min = django_filters.NumberFilter(field_name="risk_score__risk_score", lookup_expr="gte")
    risk_score_max = django_filters.NumberFilter(field_name="risk_score__risk_score", lookup_expr="lte")
    mileage_max = django_filters.NumberFilter(field_name="mileage", lookup_expr="lte")
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Vehicle
        fields = ["brand", "model", "year", "fuel_type", "status"]

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(vin_code__icontains=value)
            | Q(plate_number__icontains=value)
            | Q(brand__icontains=value)
            | Q(model__icontains=value)
        )