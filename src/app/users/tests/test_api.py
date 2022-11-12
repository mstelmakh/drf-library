from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient


ACCOUNT_URL = reverse('users:account')


class UnauthenticatedApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_account_auth_required(self):
        res = self.client.get(ACCOUNT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedApiTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_account(self):
        res = self.client.get(ACCOUNT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        empty_account = {
            'first_name': '',
            'last_name': '',
            'email': ''
        }
        self.assertEqual(res.data, empty_account)

    def test_update_account(self):
        payload = {
            'first_name': "John",
            'last_name': "Doe",
            'email': "test@gmail.com"
        }
        res = self.client.put(ACCOUNT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        for field in payload:
            self.assertEqual(self.user.__dict__[field], payload[field])

    def test_partial_update_account(self):
        payload = {
            'first_name': "Jane",
        }
        res = self.client.patch(ACCOUNT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, payload['first_name'])
