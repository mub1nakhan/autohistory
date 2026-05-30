from rest_framework.routers import DefaultRouter
from .views import AccidentViewSet

router = DefaultRouter()
router.register(r'accidents', AccidentViewSet, basename='accident')

urlpatterns = router.urls