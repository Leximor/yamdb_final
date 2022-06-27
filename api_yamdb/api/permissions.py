from rest_framework import permissions

from users.models import UserRole


class AuthorOrModeratorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return request.method in permissions.SAFE_METHODS
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return request.method in permissions.SAFE_METHODS
        return (
            obj.author == request.user
            or request.user.role == UserRole.MODERATOR.value
            or request.user.role == UserRole.ADMIN.value
            or request.user.is_superuser
        )


class AdministratorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return request.method in permissions.SAFE_METHODS
        return (
            request.user.role == UserRole.ADMIN.value
            or request.user.is_superuser
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return request.method in permissions.SAFE_METHODS
        return (
            request.user.role == UserRole.ADMIN.value
            or request.user.is_superuser
        )


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (request.user.role == UserRole.ADMIN.value
                    or request.user.is_superuser)
        return False
