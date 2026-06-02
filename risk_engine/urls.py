from rest_framework.routers import DefaultRouter
from .views import RiskScoreViewSet

router = DefaultRouter()
router.register(r"", RiskScoreViewSet, basename="api-risk-score")

urlpatterns = router.urls