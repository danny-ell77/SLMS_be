from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


cookie_details = dict(
    key=settings.SIMPLE_JWT['AUTH_COOKIE'],
    expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
    httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
    samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
)
print(cookie_details)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return dict(
        refresh=str(refresh),
        access=str(refresh.access_token)
    )


def populate_model(data, model):
    for name, value in data.items():
        if hasattr(model, name):
            setattr(model, name, value)
    return model
