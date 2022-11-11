from rest_framework import serializers

from library.models import (
    Language,
    Genre,
    Author,
    Book,
    BookInstance
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


class BaseBookInstanceSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')

    class Meta:
        abstract = True


class BookInstanceSerializer(BaseBookInstanceSerializer):
    class Meta:
        model = BookInstance
        fields = (
            'id',
            'book',
            'due_back',
            'status',
        )
        read_only_fields = ('id', )


class BookInstanceLibrarianSerializer(BaseBookInstanceSerializer):
    class Meta:
        model = BookInstance
        fields = (
            'id',
            'book',
            'borrower',
            'due_back',
            'status',
        )
        read_only_fields = ('id', )
