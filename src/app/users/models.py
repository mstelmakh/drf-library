from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    roles = models.ManyToManyField(Role)
