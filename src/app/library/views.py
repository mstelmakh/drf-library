from uuid import uuid4
from rest_framework import viewsets, views

from library.permissions import IsAdminOrReadOnly, IsLibrarian, IsUser

from library.models import (
    Genre,
    Language,
    Author,
    Book,
    BookInstance
)

from library.serializers import (
    GenreSerializer,
    LanguageSerializer,
    AuthorSerializer,
    BookSerializer,
    BookInstanceSerializer,
    BookInstanceLibrarianSerializer
)

from users.services import is_librarian


class GenreViewSet(viewsets.ModelViewSet):
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly, )
    queryset = Genre.objects.all()


class LanguageViewSet(viewsets.ModelViewSet):
    serializer_class = LanguageSerializer
    permission_classes = (IsAdminOrReadOnly, )
    queryset = Language.objects.all()


class AuthorViewSet(viewsets.ModelViewSet):
    serializer_class = AuthorSerializer
    permission_classes = (IsAdminOrReadOnly, )
    queryset = Author.objects.all()


class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrReadOnly, )
    queryset = Book.objects.all()


class BookInstanceViewSet(viewsets.ModelViewSet):
    serializer_class = BookInstanceSerializer
    permission_classes = (IsAdminOrReadOnly, )
    queryset = BookInstance.objects.all()

    def get_serializer_class(self):
        if is_librarian(self.request.user):
            return BookInstanceLibrarianSerializer
        else:
            return BookInstanceSerializer


class ReserveBookView(views.APIView):
    permission_classes = (IsUser, )

    def post(self, request, format=None, **kwargs):
        book_instance_id: uuid4 = self.kwargs.get("id")
        user_id: int = request.user.id
        print(f"{book_instance_id=}, {user_id=}")
        # reserve_book(book_id, user_id)


class CancelBookReservationView(views.APIView):
    permission_classes = (IsUser, )

    def post(self, request, format=None):
        pass


class UpdateBookStatusView(views.APIView):
    permission_classes = (IsLibrarian, )

    def post(self, request, format=None):
        pass


class RenewBookView(views.APIView):
    permission_classes = (IsLibrarian, )

    def post(self, request, format=None):
        pass
