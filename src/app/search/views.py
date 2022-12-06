import abc

from django.http import HttpResponse
from elasticsearch_dsl import Q
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView

from library.documents import (
    GenreDocument,
    LanguageDocument,
    AuthorDocument,
    BookDocument,
    BookInstanceDocument
)
from library.serializers import (
    GenreSerializer,
    LanguageSerializer,
    AuthorSerializer,
    BookSerializer,
    BookInstanceSerializer
)


class PaginatedElasticSearchAPIView(APIView, LimitOffsetPagination):
    serializer_class = None
    document_class = None

    @abc.abstractmethod
    def generate_q_expression(self, query):
        """This method should be overridden
        and return a Q() expression."""

    def get(self, request, query):
        try:
            q = self.generate_q_expression(query)
            search = self.document_class.search().query(q)
            response = search.execute()
            results = self.paginate_queryset(response, request, view=self)
            serializer = self.serializer_class(results, many=True)
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            return HttpResponse(e, status=500)


class SearchGenres(PaginatedElasticSearchAPIView):
    serializer_class = GenreSerializer
    document_class = GenreDocument

    def generate_q_expression(self, query):
        return Q(
                'multi_match', query=query,
                fields=[
                    'name'
                ], fuzziness='auto')


class SearchLanguages(PaginatedElasticSearchAPIView):
    serializer_class = LanguageSerializer
    document_class = LanguageDocument

    def generate_q_expression(self, query):
        return Q(
                'multi_match', query=query,
                fields=[
                    'name'
                ], fuzziness='auto')


class SearchAuthors(PaginatedElasticSearchAPIView):
    serializer_class = AuthorSerializer
    document_class = AuthorDocument

    def generate_q_expression(self, query):
        return Q(
                'multi_match', query=query,
                fields=[
                    'first_name',
                    'last_name'
                ], fuzziness='auto')


class SearchBooks(PaginatedElasticSearchAPIView):
    serializer_class = BookSerializer
    document_class = BookDocument

    def generate_q_expression(self, query):
        return Q(
                'multi_match', query=query,
                fields=[
                    'title',
                    'author.first_name',
                    'author.last_name',
                    'summary',
                    'genre.name',
                    'language.name'
                ], fuzziness='auto') | Q(
                    'match_phrase', isbn=query,
                )


class SearchBookInstances(PaginatedElasticSearchAPIView):
    serializer_class = BookInstanceSerializer
    document_class = BookInstanceDocument

    def generate_q_expression(self, query):
        return Q(
                'multi_match', query=query,
                fields=[
                    'book.title',
                ], fuzziness='auto') | Q(
                    'multi_match', query=query,
                    fields=[
                        'book.isbn',
                        'status'
                    ]
                )
