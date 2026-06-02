from rest_framework.routers import DefaultRouter
from .views import InspectionViewSet

router = DefaultRouter()
router.register(r"", InspectionViewSet, basename="api-inspection")

urlpatterns = router.urls