from rest_framework.routers import DefaultRouter
from .views import RiskScoreViewSet

router = DefaultRouter()
router.register(r'risk-scores', RiskScoreViewSet, basename='risk-score')

urlpatterns = router.urls