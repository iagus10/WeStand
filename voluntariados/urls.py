from django.urls import path
from . import views

urlpatterns = [
    path('inscripcion/<int:voluntariado_id>/', views.inscripcion_voluntariado, name='inscripcion_voluntariado'),
    path("ver-solicitudes/<int:voluntariado_id>/", views.ver_solicitudes, name="ver_solicitudes"),
    path('gestionar-solicitud/<int:solicitud_id>/', views.gestionar_solicitud, name='gestionar_solicitud'),
    path('detalle-aceptado/<int:voluntariado_id>/', views.voluntariado_aceptado, name='voluntariado_aceptado'),
    path('finalizar-participacion/<int:participacion_id>/', views.finalizar_participacion, name='finalizar_participacion'),
    path('finalizar-voluntariado/<int:voluntariado_id>/', views.finalizar_voluntariado, name='finalizar_voluntariado'),
    path("expulsar-participante/<int:participacion_id>/", views.expulsar_participante, name="expulsar_participante"),
    path('readmitir-participante/<int:participacion_id>/', views.readmitir_participante, name='readmitir_participante'),
    path('valorar/<int:voluntariado_id>/', views.valorar_voluntariado, name='valorar_voluntariado'),
    path("valorar-voluntario/<int:participacion_id>/", views.valorar_voluntario, name="valorar_voluntario"),
]
