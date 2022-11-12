from django.contrib.auth import get_user_model
from django.test import TestCase

from users.models import CustomUser
from users.services import is_user, is_librarian


class TestServices(TestCase):
    def test_is_user(self):
        user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
            role=CustomUser.Role.USER
        )
        self.assertTrue(is_user(user))

    def test_is_librarian(self):
        user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
            role=CustomUser.Role.LIBRARIAN
        )
        self.assertTrue(is_librarian(user))
