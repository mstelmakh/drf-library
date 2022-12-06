from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from library.models import Language

from library.serializers import LanguageSerializer


LANGUAGE_LIST_URL = reverse('library:language-list')


class PublicLanguageAPITest(TestCase):
    def setUp(self):
        self.english = Language.objects.create(name="English")
        Language.objects.create(name="French")
        self.languages = Language.objects.all()

        self.client = APIClient()

    def test_list_languages(self):
        response = self.client.get(LANGUAGE_LIST_URL)

        serializer = LanguageSerializer(self.languages, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_language(self):
        response = self.client.get(f"{LANGUAGE_LIST_URL}{self.english.id}/")

        serializer = LanguageSerializer(self.english)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_language(self):
        data = {"name": "spanish"}
        response = self.client.post(LANGUAGE_LIST_URL, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_language(self):
        data = {"name": "spanish"}
        response = self.client.put(
            f"{LANGUAGE_LIST_URL}{self.english.id}/",
            data
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateLanguageAPITest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.english = Language.objects.create(name="English")
        Language.objects.create(name="French")
        self.languages = Language.objects.all()

    def test_list_languages(self):
        response = self.client.get(LANGUAGE_LIST_URL)

        serializer = LanguageSerializer(self.languages, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_language(self):
        response = self.client.get(f"{LANGUAGE_LIST_URL}{self.english.id}/")

        serializer = LanguageSerializer(self.english)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_language(self):
        data = {"name": "spanish"}
        response = self.client.post(LANGUAGE_LIST_URL, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_language(self):
        data = {"name": "spanish"}
        response = self.client.put(
            f"{LANGUAGE_LIST_URL}{self.english.id}/",
            data
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminLanguageAPITest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
            is_staff=True
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.english = Language.objects.create(name="English")
        Language.objects.create(name="French")
        self.languages = Language.objects.all()

    def test_list_languages(self):
        response = self.client.get(LANGUAGE_LIST_URL)

        serializer = LanguageSerializer(self.languages, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_language(self):
        response = self.client.get(f"{LANGUAGE_LIST_URL}{self.english.id}/")

        serializer = LanguageSerializer(self.english)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_language(self):
        data = {"name": "spanish"}
        response = self.client.post(LANGUAGE_LIST_URL, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_language(self):
        data = {"name": "spanish"}
        response = self.client.put(
            f"{LANGUAGE_LIST_URL}{self.english.id}/",
            data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Language.objects.get(id=self.english.id).name,
            data["name"]
        )
