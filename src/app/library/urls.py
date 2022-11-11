from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()

router.register('language', views.LanguageViewSet)
router.register('genre', views.GenreViewSet)
router.register('author', views.AuthorViewSet)
router.register('book', views.BookViewSet)
router.register('book_instance', views.BookInstanceViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('book_instance/<uuid:id>/reserve/', views.ReserveBookView.as_view()),
]
