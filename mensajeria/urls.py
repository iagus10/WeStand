from django.urls import path
from mensajeria import views

app_name = 'mensajeria'

urlpatterns = [
    path('', views.mensajes, name='mensajes'),
    path('crear/', views.crear_conversacion, name='crear_conversacion'),
    path('buscar_usuarios/', views.buscar_usuarios, name='buscar_usuarios'),
    path('<int:conversacion_id>/', views.mensajes_conversacion, name='mensajes_conversacion'),
    path('salir/<int:conversacion_id>/', views.salir_conversacion, name='salir_conversacion'),
    path('enviar_mensaje/', views.enviar_mensaje, name='enviar_mensaje'),
    path('mensajes/contar-no-leidos/', views.contar_mensajes_no_leidos, name='contar_mensajes_no_leidos'),
  
]