from django.urls import path
from gestionLogin import views

urlpatterns = [
    path('login/', views.login_form, name="login_form"),  # Muestra el formulario
    path('login/auth/', views.login_view, name="login_view"),  # Procesa el login
    path('registro/submit/', views.registro_view, name='registro_form'),  # Procesa registro
    path('registro/', views.registro_view, name='registro_view'),
    path('verificar/<str:email>/', views.verificar_email_view, name="verificar_email"),

]
