import datetime
from django.utils import timezone

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from library.models import Author

from library.serializers import AuthorSerializer


AUTHOR_LIST_URL = reverse('library:author-list')


def get_formatted_date(date: str) -> datetime.date:
    return timezone.datetime.fromisoformat(date).date()


class PublicAuthorAPITest(TestCase):
    def setUp(self):
        date_of_birth1 = get_formatted_date("1970-01-01")
        date_of_birth2 = get_formatted_date("1965-12-05")
        date_of_death = get_formatted_date("2020-04-23")
        self.author = Author.objects.create(
            first_name="John",
            last_name="Doe",
            date_of_birth=date_of_birth1
        )
        Author.objects.create(
            first_name="Jane",
            last_name="Doe",
            date_of_birth=date_of_birth2,
            date_of_death=date_of_death
        )
        self.authors = Author.objects.all()

        self.client = APIClient()

    def test_list_authors(self):
        response = self.client.get(AUTHOR_LIST_URL)

        serializer = AuthorSerializer(self.authors, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_author(self):
        response = self.client.get(f"{AUTHOR_LIST_URL}{self.author.id}/")

        serializer = AuthorSerializer(self.author)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_author(self):
        date_of_birth = get_formatted_date("1989-07-19")

        data = {
            "first_name": "Jake",
            "last_name": "Moe",
            "date_of_birth": date_of_birth
        }
        response = self.client.post(AUTHOR_LIST_URL, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_author(self):
        date_of_birth = get_formatted_date("1989-07-19")

        data = {
            "first_name": "Jake",
            "last_name": "Moe",
            "date_of_birth": date_of_birth
        }
        response = self.client.put(
            f"{AUTHOR_LIST_URL}{self.author.id}/",
            data
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAuthorAPITest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        date_of_birth1 = get_formatted_date("1970-01-01")
        date_of_birth2 = get_formatted_date("1965-12-05")
        date_of_death = get_formatted_date("2020-04-23")
        self.author = Author.objects.create(
            first_name="John",
            last_name="Doe",
            date_of_birth=date_of_birth1
        )
        Author.objects.create(
            first_name="Jane",
            last_name="Doe",
            date_of_birth=date_of_birth2,
            date_of_death=date_of_death
        )
        self.authors = Author.objects.all()

    def test_list_authors(self):
        response = self.client.get(AUTHOR_LIST_URL)

        serializer = AuthorSerializer(self.authors, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_author(self):
        response = self.client.get(f"{AUTHOR_LIST_URL}{self.author.id}/")

        serializer = AuthorSerializer(self.author)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_author(self):
        date_of_birth = get_formatted_date("1989-07-19")

        data = {
            "first_name": "Jake",
            "last_name": "Moe",
            "date_of_birth": date_of_birth
        }
        response = self.client.post(AUTHOR_LIST_URL, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_author(self):
        date_of_birth = get_formatted_date("1989-07-19")

        data = {
            "first_name": "Jake",
            "last_name": "Moe",
            "date_of_birth": date_of_birth
        }
        response = self.client.put(
            f"{AUTHOR_LIST_URL}{self.author.id}/",
            data
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAuthorAPITest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
            is_staff=True
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        date_of_birth1 = get_formatted_date("1970-01-01")
        date_of_birth2 = get_formatted_date("1965-12-05")
        date_of_death = get_formatted_date("2020-04-23")
        self.author = Author.objects.create(
            first_name="John",
            last_name="Doe",
            date_of_birth=date_of_birth1
        )
        Author.objects.create(
            first_name="Jane",
            last_name="Doe",
            date_of_birth=date_of_birth2,
            date_of_death=date_of_death
        )
        self.authors = Author.objects.all()

    def test_list_authors(self):
        response = self.client.get(AUTHOR_LIST_URL)

        serializer = AuthorSerializer(self.authors, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_author(self):
        response = self.client.get(f"{AUTHOR_LIST_URL}{self.author.id}/")

        serializer = AuthorSerializer(self.author)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_author(self):
        date_of_birth = get_formatted_date("1989-07-19")

        data = {
            "first_name": "Jake",
            "last_name": "Moe",
            "date_of_birth": date_of_birth
        }
        response = self.client.post(AUTHOR_LIST_URL, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_author(self):
        date_of_birth = get_formatted_date("1989-07-19")

        data = {
            "first_name": "Jake",
            "last_name": "Moe",
            "date_of_birth": date_of_birth
        }
        response = self.client.put(
            f"{AUTHOR_LIST_URL}{self.author.id}/",
            data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Author.objects.get(id=self.author.id).first_name,
            data["first_name"]
        )
