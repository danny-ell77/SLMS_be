from time import time
from django.db import models
from django.contrib.auth.models import AbstractUser
from api.managers import AssignmentsManager, CourseMaterialManager, SubmissionsManager, UserManager
from django.utils import timezone

STATUS = (
    ("PENDING", "pending"),
    ("COMPLETED", "completed"),
    ("CANCELLED", "cancelled"),
)


class TimestampedModel(models.Model):
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True
        ordering = ['-created_date', '-modified_date']


class ClassRoom(TimestampedModel):
    name = models.CharField(verbose_name='class_name',
                            max_length=20, unique=True, blank=False)

    class Meta:
        verbose_name_plural = "User Classrooms"

    def __str__(self) -> str:
        return self.name


class User(AbstractUser, TimestampedModel):

    username = None
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    email = models.EmailField(unique=True)

    is_student = models.BooleanField(default=False)
    is_instructor = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def _get_fullname(self):
        fullname = f"{self.firstname} {self.lastname}"
        return fullname

    @property
    def fullname(self):
        return self._get_fullname()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.fullname


class Student(TimestampedModel, models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name='student')

    def __str__(self):
        return f"{self.user.fullname} from {self.classroom.name}"


class Instructor(TimestampedModel, models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.fullname


class Assignment(TimestampedModel, models.Model):
    question = models.CharField(max_length=300, unique=True)
    code = models.CharField(max_length=15, null=True, blank=True)
    course = models.CharField(max_length=50)
    instructor = models.ForeignKey(
        Instructor, on_delete=models.CASCADE, related_name='assignments')
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name='assignments')
    due = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, default="pending", choices=STATUS)
    marks = models.IntegerField()

    objects = AssignmentsManager()

    def __str__(self):
        return self.question

# class Courses(models.Model):
#     pass
# class Questions(TimestampedModel, models.Model):
#     title = models.CharField(max_length=300, unique=True)
#     assignment = models.ForeignKey(
#         Assignment, on_delete=models.CASCADE, related_name='questions')


class Submission(TimestampedModel, models.Model):
    content = models.TextField(blank=True)
    title = models.CharField(max_length=255, blank=False)
    status = models.CharField(max_length=15, blank=True)
    score = models.FloatField(default=0.0)
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name='submissions')
    instructor = models.ForeignKey(
        Instructor, on_delete=models.CASCADE, related_name='submissions')
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name='submissions')

    is_draft = models.BooleanField(default=False)
    is_submitted = models.BooleanField(default=False)

    objects = SubmissionsManager()

    def __str__(self):
        return self.title


class CourseMaterial(TimestampedModel, models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=120)
    course = models.CharField(max_length=120)
    document = models.FileField(null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name='course_materials', null=True)

    objects = CourseMaterialManager()

    def __str__(self):
        return self.name
