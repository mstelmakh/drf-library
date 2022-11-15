from rest_framework import serializers

from library.models import (
    Language,
    Genre,
    Author,
    Book,
    BookInstance,
    BookReservation
)


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ('id', 'name', )
        read_only_fields = ('id', )


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('id', 'name', )
        read_only_fields = ('id', )


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = (
            'id',
            'first_name',
            'last_name',
            'date_of_birth',
            'date_of_death',
        )
        read_only_fields = ('id', )


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            'id',
            'title',
            'author',
            'summary',
            'isbn',
            'genre',
            'language',
            'cover',
        )
        read_only_fields = ('id', )


class BookInstanceSerializer(serializers.ModelSerializer):
    status = serializers.ReadOnlyField(source='get_status_display')

    class Meta:
        model = BookInstance
        fields = (
            'id',
            'book',
            'status',
        )
        read_only_fields = ('id', )


class BookReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookReservation
        fields = (
            'id',
            'book_instance',
            'due_back',
            'reserved_at',
            'borrowed_at',
            'returned_at',
            'is_overdue',
        )
        read_only_fields = (
            'id',
            'reserved_at',
            'borrowed_at',
            'returned_at',
            'is_overdue',
        )


class ExtendBorrowDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookReservation
        fields = ('due_back', )
