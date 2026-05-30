from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginView, LogoutView, LogoutAllView, RegisterView, UserViewSet

router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/logout-all/", LogoutAllView.as_view(), name="auth-logout-all"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="auth-token-refresh"),
] + router.urls