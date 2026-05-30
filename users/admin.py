from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, LoginHistory


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "full_name", "role", "is_active", "is_verified", "created_at"]
    list_filter = ["role", "is_active", "is_verified", "is_staff"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone", "avatar")}),
        ("Role & status", {"fields": ("role", "is_active", "is_verified", "is_staff", "is_superuser")}),
        ("Notifications", {"fields": ("telegram_chat_id",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "role", "password1", "password2"),
        }),
    )
    filter_horizontal = ("groups", "user_permissions")


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "ip_address", "device_type", "logged_in_at", "is_active"]
    list_filter = ["is_active", "device_type"]
    search_fields = ["user__email", "ip_address"]
    readonly_fields = ["id"]