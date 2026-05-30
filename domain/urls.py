"""Service records URL patterns."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ServiceRecordViewSet

router = DefaultRouter()
router.register("", ServiceRecordViewSet, basename="service-records")

urlpatterns = [path("", include(router.urls))]