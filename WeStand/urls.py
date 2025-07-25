"""
URL configuration for WeStand project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from WeStand import views
from django.conf import settings
from django.conf.urls.static import static
from publicaciones.views import index
from django.contrib.auth.views import LogoutView



urlpatterns = [
    path("logout/", LogoutView.as_view(next_page="home"), name="logout"),
    path('admin/', admin.site.urls),
    path('', views.home, name = 'home'),
    path('index/', index, name="index"),
    path('gestionLogin/', include('gestionLogin.urls')),
    path('perfil/', include('perfil.urls')),
    path('publicaciones/', include('publicaciones.urls')),
    path('notificaciones/', include('notificaciones.urls')),
    path('mensajeria/', include('mensajeria.urls')),
    path('busqueda/', include('busqueda.urls')),
    path('voluntariados/', include('voluntariados.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)