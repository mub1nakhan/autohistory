"""Authentication and User management views."""

import logging

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend

from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserListSerializer,
    AdminUserSerializer,
    ChangePasswordSerializer,
    LoginHistorySerializer,
)
from .services import SessionService, UserService
from .permissions import IsAdmin, IsSelfOrAdmin

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
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
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
            user=user, request=request, refresh_token_jti=str(refresh["jti"])
        )
        logger.info(f"User logged in: {user.email}")
        return Response({
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
        })


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


@extend_schema_view(
    list=extend_schema(tags=["users"], summary="List users (admin only)"),
    retrieve=extend_schema(tags=["users"], summary="Get user details"),
    update=extend_schema(tags=["users"], summary="Update user"),
    partial_update=extend_schema(tags=["users"], summary="Partial update user"),
    destroy=extend_schema(tags=["users"], summary="Deactivate user"),
)
class UserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by("-created_at")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["role", "is_active", "is_verified"]
    search_fields = ["email", "first_name", "last_name"]
    ordering_fields = ["created_at", "email"]
    http_method_names = ["get", "put", "patch", "delete", "head", "options"]

    def get_permissions(self):
        if self.action == "list":
            return [IsAdmin()]
        return [IsSelfOrAdmin()]

    def get_serializer_class(self):
        if self.request.user.role == "admin":
            return AdminUserSerializer
        return UserProfileSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return User.objects.all()
        return User.objects.filter(id=user.id)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        UserService.deactivate_user(user)
        return Response({"message": "User deactivated."}, status=status.HTTP_200_OK)

    @extend_schema(tags=["users"], summary="Get current user profile")
    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        return Response(UserProfileSerializer(request.user).data)

    @extend_schema(tags=["users"], summary="Update current user profile")
    @action(detail=False, methods=["put", "patch"], url_path="me/update")
    def me_update(self, request):
        serializer = UserProfileSerializer(
            request.user, data=request.data, partial=request.method == "PATCH"
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(tags=["users"], request=ChangePasswordSerializer, summary="Change password")
    @action(detail=False, methods=["post"], url_path="me/change-password")
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        UserService.change_password(request.user, serializer.validated_data["new_password"])
        return Response({"message": "Password updated successfully."})

    @extend_schema(tags=["users"], summary="Get login history")
    @action(detail=False, methods=["get"], url_path="me/login-history")
    def login_history(self, request):
        sessions = SessionService.get_active_sessions(request.user)
        return Response(LoginHistorySerializer(sessions, many=True).data)