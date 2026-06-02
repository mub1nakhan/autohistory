from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet

router = DefaultRouter()
router.register(r"", NotificationViewSet, basename="api-notification")

urlpatterns = router.urls