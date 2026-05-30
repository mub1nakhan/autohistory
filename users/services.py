"""
Users service layer.
Business logic for user management, auth, and sessions.
"""

import logging

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from .models import LoginHistory

User = get_user_model()
logger = logging.getLogger(__name__)


class UserService:
    """Service for user domain operations."""

    @staticmethod
    def get_user_by_id(user_id):
        try:
            return User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_user_by_email(email):
        try:
            return User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return None

    @staticmethod
    def change_password(user, new_password):
        user.set_password(new_password)
        user.save(update_fields=["password", "updated_at"])
        logger.info(f"Password changed for user {user.id}")

    @staticmethod
    def update_profile(user, validated_data):
        for field, value in validated_data.items():
            setattr(user, field, value)
        user.save()
        return user

    @staticmethod
    def deactivate_user(user):
        user.is_active = False
        user.save(update_fields=["is_active", "updated_at"])
        # Logout everywhere
        SessionService.invalidate_all_sessions(user)
        logger.info(f"User {user.id} deactivated")


class SessionService:
    """Service for managing JWT sessions and login history."""

    @staticmethod
    def create_tokens(user):
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @staticmethod
    def record_login(user, request, refresh_token_jti=""):
        ip = SessionService._get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        return LoginHistory.objects.create(
            user=user,
            ip_address=ip,
            user_agent=user_agent,
            device_type=SessionService._detect_device_type(user_agent),
            refresh_token_jti=refresh_token_jti,
        )

    @staticmethod
    def record_logout(jti):
        LoginHistory.objects.filter(
            refresh_token_jti=jti, is_active=True
        ).update(is_active=False, logged_out_at=timezone.now())

    @staticmethod
    def invalidate_all_sessions(user):
        """Logout from all devices by marking all sessions inactive."""
        updated = LoginHistory.objects.filter(user=user, is_active=True).update(
            is_active=False, logged_out_at=timezone.now()
        )
        logger.info(f"Invalidated {updated} sessions for user {user.id}")
        return updated

    @staticmethod
    def get_active_sessions(user):
        return LoginHistory.objects.filter(user=user, is_active=True).order_by("-logged_in_at")

    @staticmethod
    def _get_client_ip(request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "0.0.0.0")

    @staticmethod
    def _detect_device_type(user_agent):
        ua_lower = user_agent.lower()
        if "mobile" in ua_lower or "android" in ua_lower or "iphone" in ua_lower:
            return "mobile"
        if "tablet" in ua_lower or "ipad" in ua_lower:
            return "tablet"
        return "desktop"