from uuid import uuid4
import datetime

from library.models import BookInstance, BookReservation

from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


class InvalidBookStatus(Exception):
    pass


User = get_user_model()

RESERVE_TIME_DAYS = 2
BORROW_TIME_DAYS = 31
RENEW_TIME_DAYS = 7


def get_user_reservations(user: User):
    return BookReservation.objects.filter(borrower=user)


def reserve_book(
    user: User,
    book_instance_id: uuid4,
    due_back: str
) -> BookReservation:
    book_instance = BookInstance.objects.get(pk=book_instance_id)
    if not book_instance.status == BookInstance.LoanStatus.AVAILABLE:
        raise InvalidBookStatus()
    if due_back > str(datetime.datetime.now() + datetime.timedelta(days=2)):
        raise ValidationError("Reservation can be valid for max. 2 days.")
    with transaction.atomic():
        book_instance.status = BookInstance.LoanStatus.RESERVED
        book_instance.save()

        due_back = (
            datetime.datetime.now() +
            datetime.timedelta(days=RESERVE_TIME_DAYS)
        )
        book_reservation = BookReservation.objects.create(
            book_instance=book_instance,
            borrower=user,
            due_back=due_back
        )
        return book_reservation


def cancel_reservation(reservation_id: int):
    reservation = BookReservation.objects \
                 .select_related("book_instance") \
                 .get(id=reservation_id)
    book_instance = reservation.book_instance
    if (
        not book_instance.status == BookInstance.LoanStatus.RESERVED
        or not reservation.due_back
    ):
        raise InvalidBookStatus()
    with transaction.atomic():
        book_instance.status = BookInstance.LoanStatus.AVAILABLE
        book_instance.save()

        reservation.due_back = None
        reservation.save()


def mark_borrowed(reservation_id: int, until_date: str):
    reservation = BookReservation.objects \
                 .select_related("book_instance") \
                 .get(id=reservation_id)
    book_instance = reservation.book_instance
    if until_date < str(datetime.datetime.now()):
        raise ValidationError("Due back date can't be in the past.")
    if (
        not book_instance.status == BookInstance.LoanStatus.RESERVED
        or not reservation.due_back
    ):
        raise InvalidBookStatus()
    with transaction.atomic():
        book_instance.status = BookInstance.LoanStatus.ON_LOAN
        book_instance.save()

        reservation.borrowed_at = datetime.datetime.now()
        reservation.due_back = until_date
        reservation.save()


def mark_returned(reservation_id: int):
    reservation = BookReservation.objects \
                 .select_related("book_instance") \
                 .get(id=reservation_id)
    book_instance = reservation.book_instance
    if (
        not book_instance.status == BookInstance.LoanStatus.ON_LOAN
        or not reservation.due_back
    ):
        raise InvalidBookStatus()
    with transaction.atomic():
        book_instance.status = BookInstance.LoanStatus.AVAILABLE
        book_instance.save()

        reservation.returned_at = datetime.datetime.now()
        reservation.due_back = None
        reservation.save()


def renew_reservation(reservation_id: int, until_date: str):
    reservation = BookReservation.objects \
                 .select_related("book_instance") \
                 .get(id=reservation_id)
    book_instance = reservation.book_instance
    if until_date < str(datetime.datetime.now()):
        raise ValidationError("Due back date can't be in the past.")
    if (
        not book_instance.status == BookInstance.LoanStatus.ON_LOAN
        or not reservation.due_back
    ):
        raise InvalidBookStatus()

    reservation.due_back = until_date
    reservation.save()
