from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('account/', include('users.urls')),
    path('catalog/', include('library.urls')),
    path('search/', include('search.urls')),
]
