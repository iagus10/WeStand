from django.urls import path
from . import views

urlpatterns = [
    path('me-gusta/<int:pk>/', views.toggle_like, name='toggle_megusta'),
    path('comentar/<int:pk>/', views.comentar_publicacion, name='comentar_publicacion'),
    path('eliminar/<int:pk>/', views.eliminar_publicacion, name='eliminar_publicacion'),
    path('eliminar-comentario/<int:pk>/', views.eliminar_comentario, name='eliminar_comentario'),
    path('eliminar-oferta/<int:id>/', views.eliminar_oferta_voluntariado, name='eliminar_oferta_voluntariado'),
]