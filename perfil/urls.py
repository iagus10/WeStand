from django.urls import path
from .views import perfil_view, agregar_experiencia, editar_experiencia, eliminar_experiencia, ver_perfil, toggle_seguimiento, eliminar_comentario, eliminar_oferta
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', perfil_view, name='perfil'),
    path('agregar-experiencia/', agregar_experiencia, name="agregar_experiencia"), 
    path('experiencia/<int:experiencia_id>/editar/', editar_experiencia, name='editar_experiencia'),
    path('eliminar-experiencia/<int:id>/', eliminar_experiencia, name='eliminar_experiencia'),
    path('<str:username>/', ver_perfil, name='ver_perfil'),
    path('seguir/<str:username>/', toggle_seguimiento, name='toggle_seguimiento'),
    path("eliminar-comentario/<int:id>/", eliminar_comentario, name="eliminar_comentario"),
    path('eliminar-oferta/<int:id>/', eliminar_oferta, name='eliminar_oferta'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
