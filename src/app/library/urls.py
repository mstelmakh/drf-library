from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views


app_name = "library"

router = DefaultRouter()

router.register('languages', views.LanguageViewSet)
router.register('genres', views.GenreViewSet)
router.register('authors', views.AuthorViewSet)
router.register('books', views.BookViewSet)
router.register('book_instances', views.BookInstanceViewSet)
router.register('reservations', views.ReservationViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path(
        'reservations/<int:id>/cancel/',
        views.CancelReservationView.as_view(),
        name='bookreservation-cancel'
    ),
    path(
        'reservations/<int:id>/mark_borrowed/',
        views.MarkBorrowedView.as_view(),
        name='mark-borrowed'
    ),
    path(
        'reservations/<int:id>/mark_returned/',
        views.MarkReturnedView.as_view(),
        name='mark-returned'
    ),
    path(
        'reservations/<int:id>/renew/',
        views.RenewBookView.as_view(),
        name='bookreservation-renew'
    ),
    path(
        'book_instances/<uuid:id>/subscribe/',
        views.SubscribeView.as_view(),
        name='bookinstance-subscribe'
    ),
    path(
        'book_instances/<uuid:id>/unsubscribe/',
        views.UnsubscribeView.as_view(),
        name='bookinstance-unsubscribe'
    ),
]
