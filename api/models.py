from asyncio.base_futures import _CANCELLED
from time import time
from django.db import models
from django.contrib.auth.models import AbstractUser
from api.managers import (
    AssignmentsManager,
    CourseMaterialManager,
    SubmissionsManager,
    UserManager,
)
from django.utils import timezone
from .utils import file_generate_upload_path


class TimestampedModel(models.Model):
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True
        ordering = ["-created_date", "-modified_date"]


class ClassRoom(TimestampedModel):
    name = models.CharField(
        verbose_name="class_name", max_length=20, unique=True, blank=False
    )

    class Meta:
        verbose_name_plural = "User Classrooms"

    def __str__(self) -> str:
        return self.name


class User(AbstractUser, TimestampedModel):

    username = None
    first_name = models.CharField(max_length=50, blank=False, null=False)
    last_name = models.CharField(max_length=50, blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)

    is_student = models.BooleanField(default=False)
    is_instructor = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def _get_fullname(self):
        fullname = f"{self.first_name} {self.last_name}"
        return fullname

    @property
    def fullname(self):
        return self._get_fullname()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.fullname


class Student(TimestampedModel, models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name="student"
    )
    class_representative = models.BooleanField(
        default=False
    )  # used to determine who can upload materials

    def __str__(self):
        return f"{self.user.fullname} from {self.classroom.name}"


class Instructor(TimestampedModel, models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.fullname


class Assignment(TimestampedModel, models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"
        EXPIRED = "EXPIRED", "Expired"

    question = models.CharField(max_length=300, unique=True)
    code = models.CharField(max_length=15, null=True, blank=True)
    course = models.CharField(max_length=50)
    instructor = models.ForeignKey(
        Instructor, on_delete=models.CASCADE, related_name="assignments"
    )
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name="assignments"
    )
    due = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=15, default=Status.PENDING, choices=Status.choices
    )
    marks = models.IntegerField()

    objects = AssignmentsManager()

    def __str__(self):
        return self.question


class Submission(TimestampedModel, models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        SUBMITTED = "SUBMITTED", "Submitted"

    content = models.TextField(blank=True)
    title = models.CharField(max_length=255, blank=False)
    status = models.CharField(
        max_length=15, blank=True, choices=Status.choices, default=Status.SUBMITTED
    )
    score = models.FloatField(default=0.0)
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="submissions"
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="submissions"
    )
    instructor = models.ForeignKey(
        Instructor, on_delete=models.CASCADE, related_name="submissions"
    )
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name="submissions"
    )
    remark = models.CharField(max_length=255, blank=True, null=True)

    # file = models.FileField(upload_to=file_generate_upload_path, blank=True, null=True)

    is_draft = models.BooleanField(default=False)
    is_submitted = models.BooleanField(default=False)

    objects = SubmissionsManager()

    def __str__(self):
        return self.title


class CourseMaterial(models.Model):
    file = models.FileField(upload_to=file_generate_upload_path, blank=True, null=True)

    original_file_name = models.TextField(blank=True, null=True)

    file_name = models.CharField(max_length=255, unique=True, blank=True, null=True)
    file_type = models.CharField(max_length=255, blank=True, null=True)

    upload_finished_at = models.DateTimeField(blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name="course_materials", null=True
    )

    objects = CourseMaterialManager()

    @property
    def is_valid(self):
        return bool(self.upload_finished_at)

    def __str__(self) -> str:
        return f"{self.original_file_name} for {self.classroom}"
