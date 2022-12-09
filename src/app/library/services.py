from uuid import UUID
from django.utils import timezone
from django.db import connection

from library.models import BookInstance, BookReservation

from django.conf import settings

from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.core.mail import send_mail


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
    if due_back > (
        timezone.now()
        + timezone.timedelta(days=MAX_RESERVE_TIME_DAYS)
    ).strftime("%Y-%m-%dT%H:%M"):
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

        if user in book_instance.subscribers.all():
            unsubscribe_from_book_instance(book_instance_id, user)

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
    if until_date < (timezone.now()).strftime("%Y-%m-%dT%H:%M"):
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
    if until_date < (timezone.now()).strftime("%Y-%m-%dT%H:%M"):
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


def subscribe_to_book_instance(book_instance_id: UUID, user: User) -> None:
    if not user.email:
        raise ValidationError(
            "Add email address in your account settings."
        )

    book_instance = BookInstance.objects.get(pk=book_instance_id)

    if user in book_instance.subscribers.all():
        raise ValidationError(
            "Already subscribed."
        )

    book_instance.subscribers.add(user)
    book_instance.save()
    print(connection.queries)


def unsubscribe_from_book_instance(book_instance_id: UUID, user: User) -> None:
    book_instance = BookInstance.objects.get(pk=book_instance_id)

    if user not in book_instance.subscribers.all():
        raise ValidationError(
            "Not subscribed."
        )

    book_instance.subscribers.remove(user)
    book_instance.save()


def notify_book_instance_subscribers(book_instance_id: UUID) -> None:
    book_instance = BookInstance.objects \
                    .select_related("book") \
                    .get(pk=book_instance_id)

    subject = "Status of book you are following changed!"
    message = (
            "Hello!\n"
            f"Just want to notify you, that book {book_instance.book.title} "
            "is now available.\n\n"
            "Best Regards,\n"
            "DRF Library Management Team"
        )

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email for user in book_instance.subscribers.all()],
        fail_silently=False
    )
