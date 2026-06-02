from rest_framework.routers import DefaultRouter
from .views import AnalyticsViewSet

router = DefaultRouter()
router.register(r"", AnalyticsViewSet, basename="api-analytics")

urlpatterns = router.urls