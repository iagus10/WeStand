from django import forms
from django.contrib.auth.forms import UserCreationForm
from gestionLogin.models import User 

class RegistroForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'user_type', 'password1', 'password2']
