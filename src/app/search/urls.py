from django.urls import path

from search.views import (
    SearchGenres,
    SearchLanguages,
    SearchAuthors,
    SearchBooks,
    SearchBookInstances
)

urlpatterns = [
    path('genres/<str:query>/', SearchGenres.as_view()),
    path('languages/<str:query>/', SearchLanguages.as_view()),
    path('authors/<str:query>/', SearchAuthors.as_view()),
    path('books/<str:query>/', SearchBooks.as_view()),
    path('bookinstances/<str:query>/', SearchBookInstances.as_view()),
]
