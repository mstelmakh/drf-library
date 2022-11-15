from rest_framework import (
    viewsets,
    views,
    status
)
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from users.permissions import IsLibrarian, IsUser
from library.permissions import (
    IsAdminOrReadOnly,
    IsNotDeleteMethod,
    IsReserveeOrBorrower,
    IsNotUpdateMethod
)

from library.models import (
    Genre,
    Language,
    Author,
    Book,
    BookInstance,
    BookReservation
)

from library.serializers import (
    GenreSerializer,
    LanguageSerializer,
    AuthorSerializer,
    BookSerializer,
    BookInstanceSerializer,
    BookReservationSerializer,
    ExtendBorrowDateSerializer
)

from library.services import (
    get_user_reservations,
    reserve_book,
    cancel_reservation,
    mark_borrowed,
    mark_returned,
    renew_reservation
)


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


class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = BookReservationSerializer
    # User can list/retrieve/create reservation.
    # Admin user can do anything on reservation object.
    permission_classes = (
        (IsUser & IsNotUpdateMethod & IsNotDeleteMethod) | IsAdminUser,
    )
    queryset = BookReservation.objects.all()

    def get_queryset(self):
        return get_user_reservations(self.request.user)

    def create(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        reserve_book(
            user=request.user,
            book_instance_id=self.request.data["book_instance"],
            due_back=self.request.data['due_back']
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CancelReservationView(views.APIView):
    # Only reservee or admin can cancel reservation.
    permission_classes = ((IsUser & IsReserveeOrBorrower) | IsAdminUser, )

    def post(self, request, format=None, **kwargs):
        reservation_id: int = self.kwargs.get("id")
        self.check_object_permissions(
            request,
            BookReservation.objects.get(pk=reservation_id)
        )
        cancel_reservation(reservation_id)
        return Response(status=status.HTTP_200_OK)


class MarkBorrowedView(views.APIView):
    serializer_class = ExtendBorrowDateSerializer
    permission_classes = (IsLibrarian | IsAdminUser, )

    def post(self, request, format=None, **kwargs):
        reservation_id: int = self.kwargs.get("id")
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        mark_borrowed(reservation_id, self.request.data['due_back'])
        return Response(status=status.HTTP_200_OK)


class MarkReturnedView(views.APIView):
    permission_classes = (IsLibrarian | IsAdminUser, )

    def post(self, request, format=None, **kwargs):
        reservation_id: int = self.kwargs.get("id")
        mark_returned(reservation_id)
        return Response(status=status.HTTP_200_OK)


class RenewBookView(views.APIView):
    serializer_class = ExtendBorrowDateSerializer
    permission_classes = (IsLibrarian | IsAdminUser, )

    def post(self, request, format=None, **kwargs):
        reservation_id: int = self.kwargs.get("id")
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        renew_reservation(reservation_id, self.request.data['due_back'])
        return Response(status=status.HTTP_200_OK)
