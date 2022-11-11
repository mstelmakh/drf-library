from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Role


admin.site.register(Role)


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (
            "Roles",
            {
                "fields": (
                    "roles",
                ),
            },
        ),
    )
    filter_horizontal = UserAdmin.filter_horizontal + ('roles',)


admin.site.register(CustomUser, CustomUserAdmin)
