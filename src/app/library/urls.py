from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()

router.register('language', views.LanguageViewSet)
router.register('genre', views.GenreViewSet)
router.register('author', views.AuthorViewSet)
router.register('book', views.BookViewSet)
router.register('book_instance', views.BookInstanceViewSet)
router.register('reservation', views.ReservationViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path(
        'reservation/<int:id>/cancel/',
        views.CancelReservationView.as_view()
    ),
    path(
        'reservation/<int:id>/mark_borrowed/',
        views.MarkBorrowedView.as_view()
    ),
    path(
        'reservation/<int:id>/mark_returned/',
        views.MarkReturnedView.as_view()
    ),
    path(
        'reservation/<int:id>/renew/',
        views.RenewBookView.as_view()
    ),
]
