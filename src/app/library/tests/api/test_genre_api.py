from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from library.models import Genre

from library.serializers import GenreSerializer


GENRE_LIST_URL = reverse('library:genre-list')


class PublicGenreAPITest(TestCase):
    def setUp(self):
        self.novel = Genre.objects.create(name="Novel")
        Genre.objects.create(name="Science Fiction")
        self.genres = Genre.objects.all()

        self.client = APIClient()

    def test_list_genres(self):
        response = self.client.get(GENRE_LIST_URL)

        serializer = GenreSerializer(self.genres, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_genre(self):
        response = self.client.get(f"{GENRE_LIST_URL}{self.novel.id}/")

        serializer = GenreSerializer(self.novel)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_genre(self):
        data = {"name": "fantasy"}
        response = self.client.post(GENRE_LIST_URL, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_genre(self):
        data = {"name": "fantasy"}
        response = self.client.put(
            f"{GENRE_LIST_URL}{self.novel.id}/",
            data
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateGenreAPITest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.novel = Genre.objects.create(name="Novel")
        Genre.objects.create(name="Science Fiction")
        self.genres = Genre.objects.all()

    def test_list_genres(self):
        response = self.client.get(GENRE_LIST_URL)

        serializer = GenreSerializer(self.genres, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_genre(self):
        response = self.client.get(f"{GENRE_LIST_URL}{self.novel.id}/")

        serializer = GenreSerializer(self.novel)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_genre(self):
        data = {"name": "fantasy"}
        response = self.client.post(GENRE_LIST_URL, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_genre(self):
        data = {"name": "fantasy"}
        response = self.client.put(
            f"{GENRE_LIST_URL}{self.novel.id}/",
            data
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminGenreAPITest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
            is_staff=True
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.novel = Genre.objects.create(name="Novel")
        Genre.objects.create(name="Science Fiction")
        self.genres = Genre.objects.all()

    def test_list_genres(self):
        response = self.client.get(GENRE_LIST_URL)

        serializer = GenreSerializer(self.genres, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_genre(self):
        response = self.client.get(f"{GENRE_LIST_URL}{self.novel.id}/")

        serializer = GenreSerializer(self.novel)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_genre(self):
        data = {"name": "fantasy"}
        response = self.client.post(GENRE_LIST_URL, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_genre(self):
        data = {"name": "fantasy"}
        response = self.client.put(
            f"{GENRE_LIST_URL}{self.novel.id}/",
            data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Genre.objects.get(id=self.novel.id).name,
            data["name"]
        )
