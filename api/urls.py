from django.urls import path
from api.views import (
    CookieTokenRefreshView,
    UserRegistrationView,
    UserLoginView,
    SubmissionListView,
    SubmissionsDetailView,
    AssignmentsDetailView,
    AssignmentsListView,
    CourseMaterialsListView,
    CourseMaterialFinishUpload,
    CourseMaterialStartUpload,
    AccountInformation,
)

urlpatterns = [
    path("token/refresh", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("register", UserRegistrationView.as_view(), name="register"),
    path("login", UserLoginView.as_view(), name="login"),
    path("assignments/<int:pk>", AssignmentsDetailView.as_view()),
    path("assignments", AssignmentsListView.as_view()),
    path("submissions/<int:pk>", SubmissionsDetailView.as_view()),
    path("submissions", SubmissionListView.as_view()),
    path("course-materials", CourseMaterialsListView.as_view()),
    path("course-material/start_upload", CourseMaterialStartUpload.as_view()),
    path("course-material/finish_upload", CourseMaterialFinishUpload.as_view()),
    path("profile", AccountInformation.as_view()),
]
