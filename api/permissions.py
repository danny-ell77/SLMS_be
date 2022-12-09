from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import User
from django.shortcuts import get_object_or_404


class IsInstructorOrReadOnly(BasePermission):
    edit_methods = ("PUT", "PATCH", "POST")

    def has_permission(self, request, view):
        print("executed--")
        user = get_object_or_404(User, pk=request.user.pk)
        if request.user.is_superuser:
            return True

        if request.method in SAFE_METHODS:
            return True

        # if obj.instructor is user.instructor:
        #     return True

        if user.is_instructor and request.method in self.edit_methods:
            return True
        return False


class IsStudentOrReadOnly(BasePermission):
    edit_methods = ("PUT", "PATCH", "POST")

    def has_permission(self, request, view):
        user = get_object_or_404(User, pk=request.user.pk)
        if request.user.is_superuser:
            return True

        if request.method in SAFE_METHODS:
            return True

        # if obj.instructor is user.instructor:
        #     return True

        if user.is_student and request.method in self.edit_methods:
            return True
        return False
