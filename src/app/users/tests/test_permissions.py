from django.test import RequestFactory, TestCase

from django.contrib.auth import get_user_model

from users.permissions import IsUser, IsLibrarian

from users.models import CustomUser


class TestPermissions(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
        )
        self.factory = RequestFactory()

    def is_allowed(self, permission_class) -> bool:
        request = self.factory.delete('/')
        request.user = self.user

        permission_check = permission_class()
        permission = permission_check.has_permission(request, None)

        return permission

    def test_is_user_on_user(self):
        self.user.role = CustomUser.Role.USER
        self.user.save()

        is_allowed = self.is_allowed(IsUser)

        self.assertTrue(is_allowed)

    def test_is_user_on_librarian(self):
        self.user.role = CustomUser.Role.LIBRARIAN
        self.user.save()

        is_allowed = self.is_allowed(IsUser)

        self.assertFalse(is_allowed)

    def test_is_librarian_on_librarian(self):
        self.user.role = CustomUser.Role.LIBRARIAN
        self.user.save()

        is_allowed = self.is_allowed(IsLibrarian)

        self.assertTrue(is_allowed)

    def test_is_librarian_on_user(self):
        self.user.role = CustomUser.Role.USER
        self.user.save()

        is_allowed = self.is_allowed(IsLibrarian)

        self.assertFalse(is_allowed)
