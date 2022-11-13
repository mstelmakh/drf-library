from abc import ABC, abstractmethod

from django.utils import timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.exceptions import ValidationError

from library.services import (
    InvalidBookStatusError,
    MAX_RESERVE_TIME_DAYS,
    reserve_book,
    cancel_reservation,
    mark_borrowed,
    mark_returned,
    renew_reservation
)

from library.models import (
    Genre,
    Language,
    Author,
    Book,
    BookInstance,
    BookReservation
)


class BaseServicesTest(ABC, TestCase):
    """Base test case which creates book instance at setup."""

    @abstractmethod
    def refresh_db(self):
        pass

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass"
        )
        genre_science_fiction = Genre.objects.create(
            name="Science Fiction"
        )
        genre_novel = Genre.objects.create(
            name="Novel"
        )
        self.book = Book.objects.create(
            title="testbook",
            author=Author.objects.create(
                first_name="testauthorfirst",
                last_name="testauthorlast",
                date_of_birth="1970-01-01"
            ),
            summary="testsummary",
            isbn="1234567891234",
            language=Language.objects.create(
                name="English"
            )
        )
        self.book.genre.add(genre_science_fiction, genre_novel)
        self.book_instance = BookInstance.objects.create(
            book=self.book,
            status=BookInstance.LoanStatus.AVAILABLE
        )


class ReserveBookServiceTest(BaseServicesTest):
    def refresh_db(self):
        self.book_instance.refresh_from_db()

    def test_reserve_book(self):
        due_back = (
            timezone.now() +
            timezone.timedelta(days=MAX_RESERVE_TIME_DAYS)
        )
        reserve_book(
            user=self.user,
            book_instance_id=self.book_instance.id,
            due_back=str(due_back)
        )
        self.refresh_db()
        reservation = BookReservation.objects.first()

        self.assertEqual(
            self.book_instance.status,
            BookInstance.LoanStatus.RESERVED
        )
        self.assertEqual(
            reservation.due_back, due_back
        )
        self.assertIsNotNone(reservation.reserved_at)
        self.assertIsNone(reservation.borrowed_at)
        self.assertIsNone(reservation.returned_at)
        self.assertFalse(reservation.is_overdue)

    def test_reserve_book_invalid_status(self):
        for status in BookInstance.LoanStatus:
            if not status == BookInstance.LoanStatus.AVAILABLE:
                with self.subTest(status=status):
                    self.book_instance.status = status
                    self.book_instance.save()

                    due_back = (
                        timezone.now() +
                        timezone.timedelta(days=MAX_RESERVE_TIME_DAYS)
                    )
                    with self.assertRaises(InvalidBookStatusError):
                        reserve_book(
                            user=self.user,
                            book_instance_id=self.book_instance.id,
                            due_back=str(due_back)
                        )
                    self.assertFalse(BookReservation.objects.exists())

    def test_reserve_book_due_date_in_past(self):
        due_back = (
            timezone.now() -
            timezone.timedelta(days=1)
        )
        with self.assertRaises(ValidationError):
            reserve_book(
                user=self.user,
                book_instance_id=self.book_instance.id,
                due_back=str(due_back)
            )
        self.assertFalse(BookReservation.objects.exists())

    def test_reserve_book_due_date_more_than_max(self):
        due_back = (
            timezone.now() +
            timezone.timedelta(days=MAX_RESERVE_TIME_DAYS+1)
        )
        with self.assertRaises(ValidationError):
            reserve_book(
                user=self.user,
                book_instance_id=self.book_instance.id,
                due_back=str(due_back)
            )
        self.assertFalse(BookReservation.objects.exists())


class BaseReservedServicesTestCase(BaseServicesTest):
    """Base test case which creates and reserves book instance at setup."""
    def reserve_book(self):
        due_back = (
            timezone.now() +
            timezone.timedelta(days=MAX_RESERVE_TIME_DAYS)
        )
        reservation = reserve_book(
            user=self.user,
            book_instance_id=self.book_instance.id,
            due_back=str(due_back)
        )
        return reservation

    def setUp(self):
        super().setUp()
        self.reservation = self.reserve_book()
        self.refresh_db()

    def refresh_db(self):
        self.book_instance.refresh_from_db()
        self.reservation.refresh_from_db()


class CancelReservationServiceTest(BaseReservedServicesTestCase):
    def test_cancel_reservation(self):
        cancel_reservation(self.reservation.id)
        self.refresh_db()

        reservation = BookReservation.objects.first()

        self.assertEqual(
            self.book_instance.status,
            BookInstance.LoanStatus.AVAILABLE
        )
        self.assertIsNone(reservation.due_back)
        self.assertIsNotNone(reservation.reserved_at)
        self.assertIsNone(reservation.borrowed_at)
        self.assertIsNone(reservation.returned_at)
        self.assertFalse(reservation.is_overdue)

    def test_cancel_reservation_invalid_book_status(self):
        for status in BookInstance.LoanStatus:

            if not status == BookInstance.LoanStatus.RESERVED:
                with self.subTest(status=status):
                    self.book_instance.status = status
                    self.book_instance.save()

                    with self.assertRaises(InvalidBookStatusError):
                        cancel_reservation(self.reservation.id)

    def test_cancel_wrong_reservation(self):
        # Canceling first reservation
        cancel_reservation(self.reservation.id)
        self.refresh_db()
        # Second reservation
        self.reserve_book()
        self.refresh_db()
        # Trying to cancel first reservation
        with self.assertRaises(ValidationError):
            cancel_reservation(self.reservation.id)

    class MarkBorrowedServiceTest(BaseReservedServicesTestCase):
        def setUp(self):
            super().setUp()
            self.valid_until_date = (
                timezone.now() +
                timezone.timedelta(days=5)
            )

        def test_mark_borrowed(self):
            mark_borrowed(self.reservation.id, str(self.valid_until_date))
            self.refresh_db()

            reservation = BookReservation.objects.first()

            self.assertEqual(
                self.book_instance.status,
                BookInstance.LoanStatus.ON_LOAN
            )
            self.assertEqual(reservation.due_back, self.valid_until_date)
            self.assertIsNotNone(reservation.reserved_at)
            self.assertIsNotNone(reservation.borrowed_at)
            self.assertIsNone(reservation.returned_at)
            self.assertFalse(reservation.is_overdue)

        def test_mark_borrowed_invalid_book_status(self):
            for status in BookInstance.LoanStatus:

                if not status == BookInstance.LoanStatus.RESERVED:
                    with self.subTest(status=status):
                        self.book_instance.status = status
                        self.book_instance.save()

                        with self.assertRaises(InvalidBookStatusError):
                            mark_borrowed(
                                reservation_id=self.reservation.id,
                                until_date=self.valid_until_date
                            )

        def test_mark_borrowed_wrong_reservation(self):
            # Canceling first reservation
            cancel_reservation(self.reservation.id)
            self.refresh_db()
            # Second reservation
            self.reserve_book()
            self.refresh_db()
            # Trying to borrow book from first reservation
            with self.assertRaises(ValidationError):
                mark_borrowed(
                    reservation_id=self.reservation.id,
                    until_date=self.valid_until_date
                )

        def test_mark_borrowed_until_date_in_past(self):
            until_date = (
                timezone.now() -
                timezone.timedelta(days=1)
            )
            with self.assertRaises(ValidationError):
                mark_borrowed(
                    reservation_id=self.reservation.id,
                    until_date=until_date
                )

    class RenewReservationServiceTest(BaseReservedServicesTestCase):
        def setUp(self):
            super().setUp()
            self.valid_until_date = (
                timezone.now() +
                timezone.timedelta(days=10)
            )

        def test_renew_reservation_reserved(self):
            renew_reservation(self.reservation.id, str(self.valid_until_date))
            self.refresh_db()

            reservation = BookReservation.objects.first()

            self.assertEqual(
                self.book_instance.status,
                BookInstance.LoanStatus.RESERVED
            )
            self.assertEqual(reservation.due_back, self.valid_until_date)
            self.assertIsNotNone(reservation.reserved_at)
            self.assertIsNone(reservation.borrowed_at)
            self.assertIsNone(reservation.returned_at)
            self.assertFalse(reservation.is_overdue)

        def test_renew_reservation_borrowed(self):
            borrowed_until_date = (
                timezone.now() +
                timezone.timedelta(days=5)
            )
            mark_borrowed(self.reservation.id, str(borrowed_until_date))
            self.refresh_db()

            renew_reservation(self.reservation.id, str(self.valid_until_date))
            self.refresh_db()

            reservation = BookReservation.objects.first()

            self.assertEqual(
                self.book_instance.status,
                BookInstance.LoanStatus.ON_LOAN
            )
            self.assertEqual(reservation.due_back, self.valid_until_date)
            self.assertIsNotNone(reservation.reserved_at)
            self.assertIsNotNone(reservation.borrowed_at)
            self.assertIsNone(reservation.returned_at)
            self.assertFalse(reservation.is_overdue)

        def test_renew_reservation_invalid_book_status(self):
            for status in BookInstance.LoanStatus:

                if status not in (
                    BookInstance.LoanStatus.RESERVED,
                    BookInstance.LoanStatus.ON_LOAN
                ):
                    with self.subTest(status=status):
                        self.book_instance.status = status
                        self.book_instance.save()

                        with self.assertRaises(InvalidBookStatusError):
                            renew_reservation(
                                reservation_id=self.reservation.id,
                                until_date=self.valid_until_date
                            )

        def test_renew_wrong_reservation(self):
            # Canceling first reservation
            cancel_reservation(self.reservation.id)
            self.refresh_db()
            # Second reservation
            self.reserve_book()
            self.refresh_db()
            # Trying to borrow book from first reservation
            with self.assertRaises(ValidationError):
                renew_reservation(
                    reservation_id=self.reservation.id,
                    until_date=self.valid_until_date
                )

        def test_renew_reservation_until_date_in_past(self):
            until_date = (
                timezone.now() -
                timezone.timedelta(days=1)
            )
            with self.assertRaises(ValidationError):
                renew_reservation(
                    reservation_id=self.reservation.id,
                    until_date=until_date
                )


class BaseBorrowedServicesTestCase(BaseReservedServicesTestCase):
    """
    Base test case which creates, reserves and
    borrows book instance at setup.
    """
    def borrow_book(self):
        until_date = (
            timezone.now() +
            timezone.timedelta(days=30)
        )
        reservation = mark_borrowed(
            reservation_id=self.reservation.id,
            until_date=str(until_date)
        )
        return reservation

    def setUp(self):
        super().setUp()
        self.reservation = self.borrow_book()
        self.refresh_db()


class MarkReturnedServiceTest(BaseBorrowedServicesTestCase):
    def test_mark_returned(self):
        mark_returned(self.reservation.id)
        self.refresh_db()

        reservation = BookReservation.objects.first()

        self.assertEqual(
            self.book_instance.status,
            BookInstance.LoanStatus.AVAILABLE
        )
        self.assertIsNone(reservation.due_back)
        self.assertIsNotNone(reservation.reserved_at)
        self.assertIsNotNone(reservation.borrowed_at)
        self.assertIsNotNone(reservation.returned_at)
        self.assertFalse(reservation.is_overdue)

    def test_mark_returned_invalid_book_status(self):
        for status in BookInstance.LoanStatus:

            if not status == BookInstance.LoanStatus.ON_LOAN:
                with self.subTest(status=status):
                    self.book_instance.status = status
                    self.book_instance.save()

                    with self.assertRaises(InvalidBookStatusError):
                        mark_returned(
                            reservation_id=self.reservation.id,
                        )

    def test_mark_returned_wrong_reservation(self):
        # Canceling first reservation
        reservation1 = mark_returned(self.reservation.id)
        self.refresh_db()
        # Second reservation
        self.reservation = self.reserve_book()
        self.refresh_db()
        self.borrow_book()
        self.refresh_db()
        # Trying to return book from first reservation
        with self.assertRaises(ValidationError):
            mark_returned(
                reservation_id=reservation1.id,
            )
