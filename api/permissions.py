from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import User


class IsInstructorOrReadOnly(BasePermission):
    edit_methods = ("PUT", "PATCH", "POST")

    def has_object_permission(self, request, view, obj):
        user = User.objects.get(pk=request.user.pk)
        if request.user.is_superuser:
            return True

        if request.method in SAFE_METHODS:
            return True

        # if obj.instructor is user.instructor:
        #     return True

        if user.instructor and request.method in self.edit_methods:
            return True
        return False


class IsStudentOrReadOnly(BasePermission):
    edit_methods = ("PUT", "PATCH", "POST")

    def has_object_permission(self, request, view, obj):
        user = User.objects.get(pk=request.user.pk)
        if request.user.is_superuser:
            return True

        if request.method in SAFE_METHODS:
            return True

        # if obj.instructor is user.instructor:
        #     return True

        if user.student and request.method in self.edit_methods:
            return True
        return False
