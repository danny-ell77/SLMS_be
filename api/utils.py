from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ImproperlyConfigured

cookie_details = dict(
    key=settings.SIMPLE_JWT["AUTH_COOKIE"],
    expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
    secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
    httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
    samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
)


def file_generate_upload_path(instance, filename):
    return f"{upload_type}/{instance.file_name}"


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return dict(refresh=str(refresh), access=str(refresh.access_token))


def populate_model(data, model):
    for name, value in data.items():
        if hasattr(model, name):
            setattr(model, name, value)
    return model


def assert_settings(required_settings, error_message_prefix=""):
    """
    Checks if each item from `required_settings` is present in Django settings
    """
    not_present = []
    values = {}

    for required_setting in required_settings:
        if not hasattr(settings, required_setting):
            not_present.append(required_setting)
            continue

        values[required_setting] = getattr(settings, required_setting)

    if not_present:
        if not error_message_prefix:
            error_message_prefix = "Required settings not found."

        stringified_not_present = ", ".join(not_present)

        raise ImproperlyConfigured(
            f"{error_message_prefix} Could not find: {stringified_not_present}"
        )

    return values


# class WritableSerializerMethodField(serializers.SerializerMethodField):
#     def __init__(self, **kwargs):
#         self.setter_method_name = kwargs.pop('setter_method_name', None)
#         self.deserializer_field = kwargs.pop('deserializer_field')

#         super().__init__(**kwargs)

#         self.read_only = False

#     def bind(self, field_name, parent):
#         retval = super().bind(field_name, parent)
#         if not self.setter_method_name:
#             self.setter_method_name = f'set_{field_name}'

#         return retval

#     def get_default(self):
#         default = super().get_default()

#         return {
#             self.field_name: default
#         }

#     def to_internal_value(self, data):
#         value = self.deserializer_field.to_internal_value(data)
#         method = getattr(self.parent, self.setter_method_name)
#         return {self.field_name: self.deserializer_field.to_internal_value(method(value))}
