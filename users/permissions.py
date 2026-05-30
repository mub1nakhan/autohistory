"""Custom permission classes for RBAC."""

from rest_framework.permissions import BasePermission, IsAuthenticated

from .models import UserRole


class IsAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == UserRole.ADMIN


class IsAdminOrInspector(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role in (
            UserRole.ADMIN, UserRole.INSPECTOR
        )


class IsAdminOrServiceCenter(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role in (
            UserRole.ADMIN, UserRole.SERVICE_CENTER
        )


class IsAdminOrDealer(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role in (
            UserRole.ADMIN, UserRole.DEALER
        )


class IsSelfOrAdmin(IsAuthenticated):
    """Allow access to own resource or admin."""

    def has_object_permission(self, request, view, obj):
        return request.user.role == UserRole.ADMIN or obj.id == request.user.id


class CanAddAccident(IsAuthenticated):
    """Only admins and inspectors can add accident records."""

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role in (
            UserRole.ADMIN, UserRole.INSPECTOR
        )


class CanAddInspection(IsAuthenticated):
    """Only admins and inspectors can add inspections."""

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role in (
            UserRole.ADMIN, UserRole.INSPECTOR
        )


class CanAddServiceRecord(IsAuthenticated):
    """Service centers and admins can add service records."""

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role in (
            UserRole.ADMIN, UserRole.SERVICE_CENTER
        )