from rest_framework.routers import DefaultRouter
from .views import ServiceRecordViewSet

router = DefaultRouter()
router.register(r'service-records', ServiceRecordViewSet, basename='service-record')

urlpatterns = router.urls