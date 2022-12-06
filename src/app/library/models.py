from django.db import models
from django.conf import settings
from django.utils import timezone

import uuid

from isbn_field import ISBNField


class Genre(models.Model):
    """
    Model representing a book genre (e.g. Science Fiction, Non Fiction).
    """
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Language(models.Model):
    """Model representing a Language (e.g. English, French, Japanese, etc.)"""
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Author(models.Model):
    """
    Model representing an author.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(
        verbose_name='died',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"


class Book(models.Model):
    """
    Model representing a book (but not a specific copy of a book).
    """
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000)
    isbn = ISBNField()
    genre = models.ManyToManyField(Genre)
    language = models.ForeignKey(
        Language,
        on_delete=models.SET_NULL,
        null=True
    )
    cover = models.ImageField(
        upload_to="upload/covers/",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title


class BookInstance(models.Model):
    """
    Model representing a specific copy of a book
    i.e. that can be borrowed from the library.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)

    class LoanStatus(models.TextChoices):
        MAINTENANCE = 'm', 'Maintenance'
        AVAILABLE = 'a', 'Available'
        RESERVED = 'r', 'Reserved'
        ON_LOAN = 'o', 'On loan'

    status = models.CharField(
        max_length=1,
        choices=LoanStatus.choices,
        default=LoanStatus.MAINTENANCE
    )

    subscribers = models.ManyToManyField(settings.AUTH_USER_MODEL)

    def __str__(self):
        return f"{self.id}, {self.book.title}"


class BookReservation(models.Model):
    book_instance = models.ForeignKey(
        BookInstance,
        on_delete=models.SET_NULL,
        null=True
    )
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    reserved_at = models.DateTimeField(auto_now_add=True)
    borrowed_at = models.DateTimeField(null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)

    due_back = models.DateTimeField(null=True, blank=True)

    @property
    def is_overdue(self):
        if self.due_back and timezone.now() > self.due_back:
            return True
        return False
