from rest_framework.routers import DefaultRouter
from .views import ServiceRecordViewSet

router = DefaultRouter()
router.register(r"", ServiceRecordViewSet, basename="api-service-record")

urlpatterns = router.urls