from django.urls import path

from users import views


urlpatterns = [
    path('', views.AccountDetail.as_view(), name='account'),
]
