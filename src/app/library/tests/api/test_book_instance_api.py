from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from library.models import BookInstance, Book, Author, Genre, Language

from library.serializers import BookInstanceSerializer


BOOK_INSTANCE_LIST_URL = reverse('library:bookinstance-list')

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

SAMPLE_BOOK_INSTANCE = {
    "book": SAMPLE_BOOK,
    "status": BookInstance.LoanStatus.AVAILABLE
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


def sample_book_instance(
    book: Book = None,
    status: BookInstance.LoanStatus = None
):
    defaults = SAMPLE_BOOK_INSTANCE.copy()

    if not book:
        book = sample_book()

    defaults["book"] = book

    if status:
        defaults["status"] = status

    book_instance = BookInstance.objects.create(**defaults)

    return book_instance


class PublicBookInstanceAPITest(TestCase):
    def setUp(self):
        self.book_instance = sample_book_instance()
        book2 = sample_book(
            title="Harry Potter and the Prisoner of Azkaban",
            isbn="0-7475-4215-5"
        )
        sample_book_instance(book=book2)

        self.book_instances = BookInstance.objects.all()

        self.client = APIClient()

    def test_list_book_instances(self):
        response = self.client.get(BOOK_INSTANCE_LIST_URL)

        serializer = BookInstanceSerializer(self.book_instances, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_book_instance(self):
        response = self.client.get(
            f"{BOOK_INSTANCE_LIST_URL}{self.book_instance.id}/"
        )

        serializer = BookInstanceSerializer(self.book_instance)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_book_instance(self):
        book = sample_book(
            title="Harry Potter and the Order of the Phoenix",
            isbn="0-7475-5100-6"
        )

        data = {
            "book": book.id,
            "status": BookInstance.LoanStatus.AVAILABLE
        }

        response = self.client.post(BOOK_INSTANCE_LIST_URL, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_book_instance(self):
        book = sample_book(
            title="Harry Potter and the Order of the Phoenix",
            isbn="0-7475-5100-6"
        )

        data = {
            "book": book.id,
            "status": BookInstance.LoanStatus.AVAILABLE
        }
        response = self.client.put(
            f"{BOOK_INSTANCE_LIST_URL}{self.book_instance.id}/",
            data
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBookInstanceAPITest(TestCase):
    def setUp(self):
        self.book_instance = sample_book_instance()
        book2 = sample_book(
            title="Harry Potter and the Prisoner of Azkaban",
            isbn="0-7475-4215-5"
        )
        sample_book_instance(book=book2)

        self.book_instances = BookInstance.objects.all()

        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_book_instances(self):
        response = self.client.get(BOOK_INSTANCE_LIST_URL)

        serializer = BookInstanceSerializer(self.book_instances, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_book_instance(self):
        response = self.client.get(
            f"{BOOK_INSTANCE_LIST_URL}{self.book_instance.id}/"
        )

        serializer = BookInstanceSerializer(self.book_instance)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_book_instance(self):
        book = sample_book(
            title="Harry Potter and the Order of the Phoenix",
            isbn="0-7475-5100-6"
        )

        data = {
            "book": book.id,
            "status": BookInstance.LoanStatus.AVAILABLE
        }

        response = self.client.post(BOOK_INSTANCE_LIST_URL, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_instance(self):
        book = sample_book(
            title="Harry Potter and the Order of the Phoenix",
            isbn="0-7475-5100-6"
        )

        data = {
            "book": book.id,
            "status": BookInstance.LoanStatus.AVAILABLE
        }
        response = self.client.put(
            f"{BOOK_INSTANCE_LIST_URL}{self.book_instance.id}/",
            data
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookInstanceAPITest(TestCase):
    def setUp(self):
        self.book_instance = sample_book_instance()
        book2 = sample_book(
            title="Harry Potter and the Prisoner of Azkaban",
            isbn="0-7475-4215-5"
        )
        sample_book_instance(book=book2)

        self.book_instances = BookInstance.objects.all()

        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
            is_staff=True
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_book_instances(self):
        response = self.client.get(BOOK_INSTANCE_LIST_URL)

        serializer = BookInstanceSerializer(self.book_instances, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_book_instance(self):
        response = self.client.get(
            f"{BOOK_INSTANCE_LIST_URL}{self.book_instance.id}/"
        )

        serializer = BookInstanceSerializer(self.book_instance)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_book_instance(self):
        book = sample_book(
            title="Harry Potter and the Order of the Phoenix",
            isbn="0-7475-5100-6"
        )

        data = {
            "book": book.id,
            "status": 'a'
        }

        response = self.client.post(BOOK_INSTANCE_LIST_URL, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_book_instance(self):
        book = sample_book(
            title="Harry Potter and the Order of the Phoenix",
            isbn="0-7475-5100-6"
        )

        data = {
            "book": book.id,
            "status": 'a'
        }
        response = self.client.put(
            f"{BOOK_INSTANCE_LIST_URL}{self.book_instance.id}/",
            data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
