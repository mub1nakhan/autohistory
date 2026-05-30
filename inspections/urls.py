from rest_framework.routers import DefaultRouter
from .views import InspectionViewSet

router = DefaultRouter()
router.register(r"inspections", InspectionViewSet, basename="inspection")

urlpatterns = router.urls