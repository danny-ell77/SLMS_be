from django.urls import path
from api.views import (
    CookieTokenRefreshView,
    UserRegistrationView,
    UserLoginView,
    SubmissionListView,
    SubmissionsDetailView,
    AssignmentsDetailView,
    AssignmentsListView
)

urlpatterns = [
    path('token/refresh', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('register', UserRegistrationView.as_view(), name='register'),
    path('login', UserLoginView.as_view(), name='login'),

    path('assignment/<int:id>/', AssignmentsDetailView.as_view()),
    path('assignments/', AssignmentsListView.as_view()),
    path('submission/<int:id>/', SubmissionsDetailView.as_view()),
    path('submissions/', SubmissionListView.as_view()),
]
