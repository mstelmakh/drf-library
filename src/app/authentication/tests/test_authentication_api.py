from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient


REGISTRATION_URL = reverse('authentication:register')
TOKEN_URL = reverse('authentication:token_obtain_pair')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class RegistrationApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_valid(self):
        data = {
            "username": "testuser",
            "password": "HardToCrack123!",
            "password2": "HardToCrack123!"
        }
        res = self.client.post(REGISTRATION_URL, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(username=data['username'])
        self.assertTrue(user.check_password(data["password"]))
        self.assertNotIn('password', res.data)

    def test_existing_username(self):
        data = {
            "username": "testuser",
            "password": "HardToCrack123!",
            "password2": "HardToCrack123!"
        }
        self.client.post(REGISTRATION_URL, data)

        res = self.client.post(REGISTRATION_URL, data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_password_too_short(self):
        data = {
            "username": "testuser",
            "password": "pas",
            "password2": "pas"
        }
        res = self.client.post(REGISTRATION_URL, data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            username=data['username']
        ).exists()
        self.assertFalse(user_exists)


class TokenTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_token_for_user(self):
        """Test that a token created for user"""
        data = {
            'username': 'test',
            'password': 'hardtocrack',
        }
        create_user(**data)
        res = self.client.post(TOKEN_URL, {'username': data['username'],
                                           'password': data['password']})
        self.assertIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credential(self):
        """Test that token is not created when
           invalid credential are given"""
        data = {
            'username': 'test',
            'password': 'hardtocrack',
        }
        create_user(**data)

        data2 = {
            'username': 'test',
            'password': 'wrong'
        }
        res = self.client.post(TOKEN_URL, data2)
        self.assertNotIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_token_no_user(self):
        """Test that token is not created if user doesn't exists"""
        data = {
            'username': 'test4',
            'password': 'testpass'
        }
        res = self.client.post(TOKEN_URL, data)

        self.assertNotIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_token_missing_field(self):
        """Test that username and password are required"""
        res = self.client.post(TOKEN_URL, {'username': 'one', 'password': ''})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
