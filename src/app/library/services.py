from uuid import UUID
from django.utils import timezone

from library.models import BookInstance, BookReservation

from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


class InvalidBookStatusError(Exception):
    pass


User = get_user_model()

MAX_RESERVE_TIME_DAYS = 2


def get_user_reservations(user: User):
    return BookReservation.objects.filter(borrower=user)


def reserve_book(
    user: User,
    book_instance_id: UUID,
    due_back: str
) -> BookReservation:
    book_instance = BookInstance.objects.get(pk=book_instance_id)
    if not book_instance.status == BookInstance.LoanStatus.AVAILABLE:
        raise InvalidBookStatusError()
    if due_back < str(timezone.now()):
        raise ValidationError("Due back date can't be in the past.")
    if due_back > str(
        timezone.now()
        + timezone.timedelta(days=MAX_RESERVE_TIME_DAYS)
    ):
        raise ValidationError(
            f"Reservation can be valid for max. {MAX_RESERVE_TIME_DAYS} days."
        )
    with transaction.atomic():
        book_instance.status = BookInstance.LoanStatus.RESERVED
        book_instance.save()

        book_reservation = BookReservation.objects.create(
            book_instance=book_instance,
            borrower=user,
            due_back=due_back
        )
        return book_reservation


def cancel_reservation(reservation_id: int) -> BookReservation:
    reservation = BookReservation.objects \
                 .select_related("book_instance") \
                 .get(id=reservation_id)
    book_instance = reservation.book_instance
    if not reservation.due_back:
        raise ValidationError("Wrong reservation id.")
    if not book_instance.status == BookInstance.LoanStatus.RESERVED:
        raise InvalidBookStatusError()
    with transaction.atomic():
        book_instance.status = BookInstance.LoanStatus.AVAILABLE
        book_instance.save()

        reservation.due_back = None
        reservation.save()
        return reservation


def mark_borrowed(reservation_id: int, until_date: str) -> BookReservation:
    reservation = BookReservation.objects \
                 .select_related("book_instance") \
                 .get(id=reservation_id)
    book_instance = reservation.book_instance
    if until_date < str(timezone.now()):
        raise ValidationError("Due back date can't be in the past.")
    if not reservation.due_back:
        raise ValidationError("Wrong reservation id.")
    if not book_instance.status == BookInstance.LoanStatus.RESERVED:
        raise InvalidBookStatusError()
    with transaction.atomic():
        book_instance.status = BookInstance.LoanStatus.ON_LOAN
        book_instance.save()

        reservation.borrowed_at = timezone.now()
        reservation.due_back = until_date
        reservation.save()
        return reservation


def mark_returned(reservation_id: int) -> BookReservation:
    reservation = BookReservation.objects \
                 .select_related("book_instance") \
                 .get(id=reservation_id)
    book_instance = reservation.book_instance
    if not reservation.due_back:
        raise ValidationError("Wrong reservation id.")
    if not book_instance.status == BookInstance.LoanStatus.ON_LOAN:
        raise InvalidBookStatusError()
    with transaction.atomic():
        book_instance.status = BookInstance.LoanStatus.AVAILABLE
        book_instance.save()

        reservation.returned_at = timezone.now()
        reservation.due_back = None
        reservation.save()
        return reservation


def renew_reservation(reservation_id: int, until_date: str) -> BookReservation:
    reservation = BookReservation.objects \
                 .select_related("book_instance") \
                 .get(id=reservation_id)
    book_instance = reservation.book_instance
    if until_date < str(timezone.now()):
        raise ValidationError("Due back date can't be in the past.")
    if not reservation.due_back:
        raise ValidationError("Wrong reservation id.")
    if book_instance.status not in (
        BookInstance.LoanStatus.ON_LOAN,
        BookInstance.LoanStatus.RESERVED
    ):
        raise InvalidBookStatusError()

    reservation.due_back = until_date
    reservation.save()
    return reservation
