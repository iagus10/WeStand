from django.urls import path
from .views import obtener_notificaciones, contar_no_leidas, marcar_notificaciones_leidas
from perfil import views as perfil_views

urlpatterns = [
    path('obtener/', obtener_notificaciones, name='obtener_notificaciones'),
    path('contar/', contar_no_leidas, name='contar_notificaciones'),
    path('marcar-leidas', marcar_notificaciones_leidas, name = 'marcar_notificaciones_leidas'),
    path('perfil/<str:username>/', perfil_views.ver_perfil, name='visitar_perfil'),
]