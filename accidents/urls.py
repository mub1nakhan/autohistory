from rest_framework.routers import DefaultRouter
from .views import AccidentViewSet

router = DefaultRouter()
router.register(r'', AccidentViewSet, basename='api-accident')

urlpatterns = router.urls