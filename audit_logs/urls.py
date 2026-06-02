from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet

router = DefaultRouter()
router.register(r"", AuditLogViewSet, basename="api-audit-log")

urlpatterns = router.urls