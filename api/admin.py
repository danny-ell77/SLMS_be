from django.contrib import admin
from api.models import User, UserClass

# Register your models here.


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    pass


admin.site.register(UserClass)
