"""User management views."""

import logging

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.users.models import User
from apps.users.permissions import IsAdmin, IsSelfOrAdmin
from apps.users.serializers import (
    AdminUserSerializer,
    ChangePasswordSerializer,
    LoginHistorySerializer,
    UserListSerializer,
    UserProfileSerializer,
)
from apps.users.services import SessionService, UserService

logger = logging.getLogger(__name__)


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
        if self.action in ["list"]:
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
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(tags=["users"], summary="Update current user profile")
    @action(detail=False, methods=["put", "patch"], url_path="me/update")
    def me_update(self, request):
        serializer = UserProfileSerializer(
            request.user, data=request.data, partial=request.method == "PATCH"
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(
        tags=["users"],
        request=ChangePasswordSerializer,
        summary="Change password",
    )
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
        serializer = LoginHistorySerializer(sessions, many=True)
        return Response(serializer.data)