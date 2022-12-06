import datetime

from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from users.models import CustomUser

from library.models import (
    BookReservation,
    BookInstance,
    Book,
    Author,
    Genre,
    Language
)

from library.serializers import BookReservationSerializer


RESERVATION_LIST_URL = reverse('library:bookreservation-list')


URLS = {
    'CANCEL_RESERVATION': 'library:bookreservation-cancel',
    'RENEW_RESERVATION': 'library:bookreservation-renew',
    'MARK_BORROWED': 'library:mark-borrowed',
    'MARK_RETURNED': 'library:mark-returned'
}


def URL(name, id):
    return reverse(URLS[name], args=(id, ))


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


def timedelta(days: int) -> datetime:
    return timezone.now() + timezone.timedelta(days=days)


SAMPLE_RESERVATION = {
    "book_instance": SAMPLE_BOOK_INSTANCE,
    "borrower": None,
    "reserved_at": timedelta(-10),
    "borrowed_at": timedelta(-9),
    "returned_at": None,
    "due_back": timedelta(20)
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


def sample_reservation(**params):
    defaults = SAMPLE_RESERVATION.copy()

    if not params.get("book_instance"):
        defaults["book_instance"] = sample_book_instance()

    defaults.update(params)

    if not defaults["borrower"]:
        username = "borrower"
        if get_user_model().objects.filter(username__exact=username).exists():
            defaults["borrower"] = get_user_model().objects.get(
                username=username
            )
        else:
            defaults["borrower"] = get_user_model().objects.create_user(
                username="borrower",
                password="testpass",
                role=CustomUser.Role.USER
            )

    reservation = BookReservation.objects.create(**defaults)
    return reservation


class PublicReservationAPITest(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
            role=CustomUser.Role.USER
        )
        self.client = APIClient()

        self.reservation = sample_reservation(borrower=user)

        book_istance2 = sample_book_instance()

        sample_reservation(
            book_instance=book_istance2,
            borrower=user,
            reserved_at=timedelta(-1),
            borrowed_at=None,
            returned_at=None,
            due_back=timedelta(1)
        )

        self.reservations = BookReservation.objects.all()

    def test_list_reservations(self):
        response = self.client.get(RESERVATION_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_reservation(self):
        response = self.client.get(
            f"{RESERVATION_LIST_URL}{self.reservation.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_reservation(self):
        book_instance = sample_book_instance()
        data = {
            "book_instance": book_instance.id,
            "due_back": timedelta(1)
        }

        response = self.client.post(RESERVATION_LIST_URL, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_reservation(self):
        book_instance = sample_book_instance()
        data = {
            "book_instance": book_instance.id,
            "due_back": timedelta(1)
        }
        response = self.client.put(
            f"{RESERVATION_LIST_URL}{self.reservation.id}/",
            data
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cancel_reservation(self):
        response = self.client.post(
            URL("CANCEL_RESERVATION", self.reservation.id)
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_renew_reservation(self):
        response = self.client.post(
            URL("RENEW_RESERVATION", self.reservation.id)
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_mark_borrowed(self):
        response = self.client.post(
            URL("MARK_BORROWED", self.reservation.id)
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_mark_returned(self):
        response = self.client.post(
            URL("MARK_RETURNED", self.reservation.id)
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserReservationAPITest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
            role=CustomUser.Role.USER
        )
        self.reservation = sample_reservation(borrower=self.user)

        book_istance2 = sample_book_instance()

        sample_reservation(
            book_instance=book_istance2,
            borrower=self.user,
            reserved_at=timedelta(-1),
            borrowed_at=None,
            returned_at=None,
            due_back=timedelta(1)
        )

        self.reservations = BookReservation.objects.all()

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_reservations(self):
        response = self.client.get(RESERVATION_LIST_URL)

        serializer = BookReservationSerializer(self.reservations, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_reservation(self):
        response = self.client.get(
            f"{RESERVATION_LIST_URL}{self.reservation.id}/"
        )

        serializer = BookReservationSerializer(self.reservation)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_reservation(self):
        book_instance = sample_book_instance()
        data = {
            "book_instance": book_instance.id,
            "due_back": timedelta(1)
        }

        response = self.client.post(RESERVATION_LIST_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_reservation(self):
        book_instance = sample_book_instance()
        data = {
            "book_instance": book_instance.id,
            "due_back": timedelta(1)
        }
        response = self.client.put(
            f"{RESERVATION_LIST_URL}{self.reservation.id}/",
            data
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cancel_reservation(self):
        book_instance = sample_book_instance(
            status=BookInstance.LoanStatus.RESERVED
        )

        reservation = sample_reservation(
            book_instance=book_instance,
            borrower=self.user
        )

        response = self.client.post(
            URL("CANCEL_RESERVATION", reservation.id)
        )
        reservation.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            reservation.book_instance.status,
            BookInstance.LoanStatus.AVAILABLE
        )

    def test_renew_reservation(self):
        response = self.client.post(
            URL("RENEW_RESERVATION", self.reservation.id)
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mark_borrowed(self):
        response = self.client.post(
            URL("MARK_BORROWED", self.reservation.id)
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mark_returned(self):
        response = self.client.post(
            URL("MARK_RETURNED", self.reservation.id)
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LibrarianReservationAPITest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
            role=CustomUser.Role.LIBRARIAN
        )
        self.reservation = sample_reservation()

        book_istance2 = sample_book_instance()

        sample_reservation(
            book_instance=book_istance2,
            reserved_at=timedelta(-1),
            borrowed_at=None,
            returned_at=None,
            due_back=timedelta(1)
        )

        self.reservations = BookReservation.objects.all()

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_reservations(self):
        response = self.client.get(RESERVATION_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_reservation(self):
        response = self.client.get(
            f"{RESERVATION_LIST_URL}{self.reservation.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_reservation(self):
        book_instance = sample_book_instance()
        data = {
            "book_instance": book_instance.id,
            "due_back": timedelta(1)
        }

        response = self.client.post(RESERVATION_LIST_URL, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_reservation(self):
        book_instance = sample_book_instance()
        data = {
            "book_instance": book_instance.id,
            "due_back": timedelta(1)
        }
        response = self.client.put(
            f"{RESERVATION_LIST_URL}{self.reservation.id}/",
            data
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cancel_reservation(self):
        response = self.client.post(
            URL("CANCEL_RESERVATION", self.reservation.id)
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_renew_reservation(self):
        book_instance = sample_book_instance(
            status=BookInstance.LoanStatus.RESERVED
        )
        reservation = sample_reservation(
            book_instance=book_instance,
            borrower=self.user
        )

        data = {
            "due_back": timedelta(10)
        }
        response = self.client.post(
            URL("RENEW_RESERVATION", reservation.id),
            data
        )
        reservation.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(reservation.due_back, data["due_back"])

    def test_mark_borrowed(self):
        book_instance = sample_book_instance(
            status=BookInstance.LoanStatus.RESERVED
        )
        reservation = sample_reservation(
            book_instance=book_instance,
            borrower=self.user
        )

        data = {
            "due_back": timedelta(10)
        }
        response = self.client.post(
            URL("MARK_BORROWED", reservation.id),
            data
        )
        reservation.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            reservation.book_instance.status,
            BookInstance.LoanStatus.ON_LOAN
        )
        self.assertEqual(reservation.due_back, data["due_back"])

    def test_mark_returned(self):
        book_instance = sample_book_instance(
            status=BookInstance.LoanStatus.RESERVED
        )
        reservation = sample_reservation(
            book_instance=book_instance,
            borrower=self.user
        )
        data = {
            "due_back": timedelta(10)
        }
        response = self.client.post(
            URL("MARK_BORROWED", reservation.id),
            data
        )
        reservation.refresh_from_db()
        self.assertEqual(
            reservation.book_instance.status,
            BookInstance.LoanStatus.ON_LOAN
        )

        response = self.client.post(
            URL("MARK_RETURNED", reservation.id),
            data
        )

        reservation.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            reservation.book_instance.status,
            BookInstance.LoanStatus.AVAILABLE
        )
        self.assertIsNone(reservation.due_back)


class AdminReservationAPITest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
            role=CustomUser.Role.USER,
            is_staff=True
        )
        self.reservation = sample_reservation(borrower=self.user)

        book_istance2 = sample_book_instance()

        sample_reservation(
            book_instance=book_istance2,
            borrower=self.user,
            reserved_at=timedelta(-1),
            borrowed_at=None,
            returned_at=None,
            due_back=timedelta(1)
        )

        self.reservations = BookReservation.objects.all()

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_reservations(self):
        response = self.client.get(RESERVATION_LIST_URL)

        serializer = BookReservationSerializer(self.reservations, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_reservation(self):
        response = self.client.get(
            f"{RESERVATION_LIST_URL}{self.reservation.id}/"
        )

        serializer = BookReservationSerializer(self.reservation)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_reservation(self):
        book_instance = sample_book_instance()
        data = {
            "book_instance": book_instance.id,
            "due_back": timedelta(1)
        }

        response = self.client.post(RESERVATION_LIST_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_reservation(self):
        book_instance = sample_book_instance()
        data = {
            "book_instance": book_instance.id,
            "due_back": timedelta(1)
        }
        response = self.client.put(
            f"{RESERVATION_LIST_URL}{self.reservation.id}/",
            data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cancel_reservation(self):
        book_instance = sample_book_instance(
            status=BookInstance.LoanStatus.RESERVED
        )

        reservation = sample_reservation(
            book_instance=book_instance,
            borrower=self.user
        )

        response = self.client.post(
            URL("CANCEL_RESERVATION", reservation.id)
        )
        reservation.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            reservation.book_instance.status,
            BookInstance.LoanStatus.AVAILABLE
        )

    def test_renew_reservation(self):
        book_instance = sample_book_instance(
            status=BookInstance.LoanStatus.RESERVED
        )
        reservation = sample_reservation(
            book_instance=book_instance,
            borrower=self.user
        )

        data = {
            "due_back": timedelta(10)
        }
        response = self.client.post(
            URL("RENEW_RESERVATION", reservation.id),
            data
        )
        reservation.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(reservation.due_back, data["due_back"])

    def test_mark_borrowed(self):
        book_instance = sample_book_instance(
            status=BookInstance.LoanStatus.RESERVED
        )
        reservation = sample_reservation(
            book_instance=book_instance,
            borrower=self.user
        )

        data = {
            "due_back": timedelta(10)
        }
        response = self.client.post(
            URL("MARK_BORROWED", reservation.id),
            data
        )
        reservation.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            reservation.book_instance.status,
            BookInstance.LoanStatus.ON_LOAN
        )
        self.assertEqual(reservation.due_back, data["due_back"])

    def test_mark_returned(self):
        book_instance = sample_book_instance(
            status=BookInstance.LoanStatus.RESERVED
        )
        reservation = sample_reservation(
            book_instance=book_instance,
            borrower=self.user
        )
        data = {
            "due_back": timedelta(10)
        }
        response = self.client.post(
            URL("MARK_BORROWED", reservation.id),
            data
        )
        reservation.refresh_from_db()
        self.assertEqual(
            reservation.book_instance.status,
            BookInstance.LoanStatus.ON_LOAN
        )

        response = self.client.post(
            URL("MARK_RETURNED", reservation.id),
            data
        )

        reservation.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            reservation.book_instance.status,
            BookInstance.LoanStatus.AVAILABLE
        )
        self.assertIsNone(reservation.due_back)
