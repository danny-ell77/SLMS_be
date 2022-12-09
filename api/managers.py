from django.contrib.auth.models import BaseUserManager
from django.db.models import Manager, Q
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class CourseMaterialManager(Manager):
    def get_course_materials(self, user):
        if user.is_student:
            print(user.student.classroom)
            # return self.filter(Q(classroom=user.student.classroom) & Q(is_valid=True))
            return self.filter(classroom=user.student.classroom)
        return self.filter(user=user)


class SubmissionsManager(Manager):
    def get_submissions(self, user):
        if user.is_instructor:
            return self.filter(instructor=user.instructor)
        return self.filter(student=user.student)


class AssignmentsManager(Manager):
    def get_assignments(self, user):
        if user.is_instructor:
            return self.filter(instructor=user.instructor)
        return self.filter(classroom=user.student.classroom)
