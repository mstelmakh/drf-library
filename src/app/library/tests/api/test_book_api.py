import os
import tempfile
from PIL import Image

from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from library.models import Book, Author, Genre, Language

from library.serializers import BookSerializer


BOOK_LIST_URL = reverse('library:book-list')

SAMPLE_AUTHOR = {
    "first_name": "Joanne",
    "last_name": "Rowling",
    "date_of_birth": timezone.datetime.fromisoformat("1965-07-31").date()
}

SAMPLE_GENRES = [
    {"name": "Fantasy"},
    {"name": "Novel"}
]

SAMPLE_LANGUAGE = {"name": "English"}

SAMPLE_BOOK = {
    "title": "Harry Potter and the Philosopher's Stone",
    "author": SAMPLE_AUTHOR,
    "summary": "Summary",
    "isbn": "0-7475-3269-9",
    "genre": SAMPLE_GENRES,
    "language": SAMPLE_LANGUAGE
}


def sample_book(**params):
    defaults = SAMPLE_BOOK.copy()
    defaults.update(params)

    author = Author.objects.create(**defaults["author"])
    language = Language.objects.create(**defaults["language"])

    defaults["author"] = author
    defaults["language"] = language

    genres = defaults["genre"]
    defaults.pop("genre")

    book = Book.objects.create(**defaults)

    for genre in genres:
        book.genre.add(Genre.objects.create(**genre))

    return book


class PublicBookAPITest(TestCase):
    def setUp(self):
        self.book = sample_book()
        sample_book(
            title="Harry Potter and the Prisoner of Azkaban",
            isbn="0-7475-4215-5",
        )
        self.books = Book.objects.all()

        self.client = APIClient()

    def test_list_books(self):
        response = self.client.get(BOOK_LIST_URL)

        serializer = BookSerializer(self.books, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_book(self):
        response = self.client.get(f"{BOOK_LIST_URL}{self.book.id}/")

        serializer = BookSerializer(self.book)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_book(self):
        genres = [genre.id for genre in self.book.genre.all()]
        data = {
            "title": "Harry Potter and the Order of the Phoenix",
            "author": self.book.author.id,
            "summary": "Summary",
            "isbn": "0-7475-5100-6",
            "language": self.book.language.id,
            "genre": genres
        }
        response = self.client.post(BOOK_LIST_URL, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_book(self):
        data = {
            "title": "Harry Potter and the Order of the Phoenix",
            "isbn": "0-7475-5100-6",
        }
        response = self.client.put(
            f"{BOOK_LIST_URL}{self.book.id}/",
            data
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBookAPITest(TestCase):
    def setUp(self):
        self.book = sample_book()
        sample_book(
            title="Harry Potter and the Prisoner of Azkaban",
            isbn="0-7475-4215-5",
        )
        self.books = Book.objects.all()

        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_books(self):
        response = self.client.get(BOOK_LIST_URL)

        serializer = BookSerializer(self.books, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_book(self):
        response = self.client.get(f"{BOOK_LIST_URL}{self.book.id}/")

        serializer = BookSerializer(self.book)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_book(self):
        genres = [genre.id for genre in self.book.genre.all()]
        data = {
            "title": "Harry Potter and the Order of the Phoenix",
            "author": self.book.author.id,
            "summary": "Summary",
            "isbn": "0-7475-5100-6",
            "language": self.book.language.id,
            "genre": genres
        }
        response = self.client.post(BOOK_LIST_URL, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book(self):
        data = {
            "title": "Harry Potter and the Order of the Phoenix",
            "isbn": "0-7475-5100-6",
        }
        response = self.client.put(
            f"{BOOK_LIST_URL}{self.book.id}/",
            data
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookAPITest(TestCase):
    def setUp(self):
        self.book = sample_book()
        sample_book(
            title="Harry Potter and the Prisoner of Azkaban",
            isbn="0-7475-4215-5",
        )
        self.books = Book.objects.all()

        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
            is_staff=True
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_books(self):
        response = self.client.get(BOOK_LIST_URL)

        serializer = BookSerializer(self.books, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_book(self):
        response = self.client.get(f"{BOOK_LIST_URL}{self.book.id}/")

        serializer = BookSerializer(self.book)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_book(self):
        genres = [genre.id for genre in self.book.genre.all()]
        data = {
            "title": "Harry Potter and the Order of the Phoenix",
            "author": self.book.author.id,
            "summary": "Summary",
            "isbn": "0-7475-5100-6",
            "language": self.book.language.id,
            "genre": genres
        }
        response = self.client.post(BOOK_LIST_URL, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_book_with_image(self):
        genres = [genre.id for genre in self.book.genre.all()]
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            data = {
                "title": "Harry Potter and the Order of the Phoenix",
                "author": self.book.author.id,
                "summary": "Summary",
                "isbn": "0-7475-5100-6",
                "language": self.book.language.id,
                "genre": genres,
                "cover": ntf
            }
            response = self.client.post(
                BOOK_LIST_URL, data, format='multipart'
            )

        book = Book.objects.get(id=response.data['id'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(os.path.exists(book.cover.path))
        book.cover.delete()

    def test_update_book(self):
        genres = [genre.id for genre in self.book.genre.all()]
        data = {
            "title": "Harry Potter and the Order of the Phoenix",
            "author": self.book.author.id,
            "summary": "Summary",
            "isbn": "0-7475-5100-6",
            "language": self.book.language.id,
            "genre": genres
        }

        response = self.client.put(
            f"{BOOK_LIST_URL}{self.book.id}/",
            data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
