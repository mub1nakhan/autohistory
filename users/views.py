"""Authentication views — login, register, logout, token refresh."""

import logging

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import viewsets
from .serializers import UserSerializer

from .models import User
from .services import SessionService, UserService

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    """Register a new user account."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["auth"],
        request=UserRegistrationSerializer,
        responses={201: UserRegistrationSerializer},
        summary="Register new user",
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        tokens = SessionService.create_tokens(user)
        refresh = RefreshToken.for_user(user)
        SessionService.record_login(
            user=user,
            request=request,
            refresh_token_jti=str(refresh["jti"]),
        )

        logger.info(f"New user registered: {user.email}")
        return Response(
            {
                "message": "Registration successful.",
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                },
                "tokens": tokens,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Login with email and password, returns JWT tokens."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["auth"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "password": {"type": "string"},
                },
                "required": ["email", "password"],
            }
        },
        summary="Login",
    )
    def post(self, request):
        email = request.data.get("email", "").strip().lower()
        password = request.data.get("password", "")

        if not email or not password:
            return Response(
                {"error": {"code": "MISSING_CREDENTIALS", "message": "Email and password are required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = UserService.get_user_by_email(email)
        if not user or not user.check_password(password):
            return Response(
                {"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid email or password."}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"error": {"code": "ACCOUNT_DISABLED", "message": "Your account has been disabled."}},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        SessionService.record_login(
            user=user,
            request=request,
            refresh_token_jti=str(refresh["jti"]),
        )

        logger.info(f"User logged in: {user.email}")
        return Response(
            {
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                },
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            }
        )


class LogoutView(APIView):
    """Logout: blacklist the refresh token."""

    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["auth"], summary="Logout current session")
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"error": {"code": "MISSING_TOKEN", "message": "Refresh token is required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            jti = token["jti"]
            token.blacklist()
            SessionService.record_logout(jti)
        except TokenError as e:
            return Response(
                {"error": {"code": "INVALID_TOKEN", "message": str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"message": "Successfully logged out."})


class LogoutAllView(APIView):
    """Logout from all devices."""

    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["auth"], summary="Logout from all devices")
    def post(self, request):
        count = SessionService.invalidate_all_sessions(request.user)
        return Response({"message": f"Logged out from {count} device(s)."})


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]