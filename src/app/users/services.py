from users.models import CustomUser
from django.contrib.auth import get_user_model


User = get_user_model()


def is_user(user: CustomUser) -> bool:
    if user.is_anonymous:
        return False
    return user.role == CustomUser.Role.USER


def is_librarian(user: CustomUser) -> bool:
    if user.is_anonymous:
        return False
    return user.role == CustomUser.Role.LIBRARIAN
