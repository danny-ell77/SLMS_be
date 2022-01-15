from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user model where the email address is the unique identifier
    and has an is_admin field to allow access to the admin app 
    """

    def create_user(self, email, password, _class, **extra_fields):
        if not email:
            raise ValueError(_("The email must be set"))
        if not password:
            raise ValueError(_("The password must be set"))
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user._class = _class
        user.save()
        return user

    def create_superuser(self, email, password, _class, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('role') != 'ADMIN':
            raise ValueError('Superuser must have role of Global Admin')
        return self.create_user(email, password, _class, **extra_fields)
