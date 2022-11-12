from django.urls import path

from users import views

app_name = "users"

urlpatterns = [
    path('', views.AccountDetail.as_view(), name='account'),
]
