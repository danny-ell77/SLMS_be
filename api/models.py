from django.db import models
from django.contrib.auth.models import AbstractUser
from api.managers import UserManager


class TimestampedModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_date', '-modified_date']


class ClassRoom(TimestampedModel):
    name = models.CharField(verbose_name='class_name',
                            max_length=20, unique=True, blank=False)

    class Meta:
        verbose_name_plural = "User Classes"

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
        return self.email


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name='student')


class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Assignment(models.Model):
    title = models.CharField(max_length=300)
    course = models.CharField(max_length=50)
    course_code = models.CharField(max_length=10)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='assignments')
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name='assignments')
    # duration = models.DateTimeField(blank=True)
    status = models.CharField(max_length=15)
    marks = models.IntegerField()

    def __str__(self):
        return self.title


class Submissions(TimestampedModel, models.Model):
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name='submissions')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='submissions')
    classroom = models.ForeignKey(
        ClassRoom, on_delete=models.CASCADE, related_name='submissions')
    content = models.TextField()
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=15)
    score = models.FloatField()

    is_draft = models.BooleanField(default=False)
    is_submitted = models.BooleanField(default=False)

    def __str__(self):
        return self.title
