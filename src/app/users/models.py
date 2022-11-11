from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    class Role(models.TextChoices):
        USER = 'U', _("User")
        LIBRARIAN = "L", _("Librarian")

    role = models.CharField(
        max_length=1,
        choices=Role.choices,
        default=Role.USER
    )
