from django.db import models
from django.conf import settings

import uuid
from datetime import date

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
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('a', 'Available'),
        ('r', 'Reserved'),
        ('o', 'On loan'),
    )

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m'
    )

    def __str__(self):
        return f"{self.id}, {self.book.title}"
