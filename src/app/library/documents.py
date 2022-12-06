from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from library.models import Genre, Language, Author, Book, BookInstance


@registry.register_document
class GenreDocument(Document):
    class Index:
        name = 'genres'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Genre
        fields = [
            'id',
            'name'
        ]


@registry.register_document
class LanguageDocument(Document):
    class Index:
        name = 'languages'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Language
        fields = [
            'id',
            'name'
        ]


@registry.register_document
class AuthorDocument(Document):
    class Index:
        name = 'authors'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Author
        fields = [
            'id',
            'first_name',
            'last_name',
        ]


@registry.register_document
class BookDocument(Document):
    author = fields.ObjectField(properties={
        'pk': fields.IntegerField(),
        'first_name': fields.TextField(),
        'last_name': fields.TextField(),
    })

    genre = fields.ObjectField(properties={
        'pk': fields.IntegerField(),
        'name': fields.TextField(),
    }, multi=True)

    language = fields.ObjectField(properties={
        'pk': fields.IntegerField(),
        'name': fields.TextField(),
    })

    isbn = fields.TextField()

    class Index:
        name = 'books'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Book
        fields = [
            'id',
            'title',
            'summary',
        ]

    def get_queryset(self):
        return super().get_queryset().select_related(
            'genre', 'language', 'author'
        )


@registry.register_document
class BookInstanceDocument(Document):
    book = fields.ObjectField(properties={
        'pk': fields.IntegerField(),
        'title': fields.TextField(),
        'isbn': fields.TextField()
    })

    status = fields.TextField(attr='get_status_display')

    class Index:
        name = 'book_instances'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = BookInstance
        fields = [
            'id',
        ]

    def get_queryset(self):
        return super().get_queryset().select_related(
            'book'
        )
