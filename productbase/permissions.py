from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    """普通用户只能操作自己的配置；管理员（is_superuser）可操作全部"""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.user == request.user
