from django import forms
from .models import Publicacion
from voluntariados.models import Voluntariado
from django.forms.widgets import ClearableFileInput

class PublicacionForm(forms.ModelForm):
    class Meta:
        model = Publicacion
        fields = ['contenido', 'imagen']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '¿En qué estás pensando?',
                'rows': 3
            }),
            'imagen': ClearableFileInput(attrs={'class': 'form-control'})
        }

class VoluntariadoForm(forms.ModelForm):
    class Meta:
        model = Voluntariado
        fields = ['nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'duracion', 'ubicacion', 'latitud', 'longitud', 'foto', 'categorias', 'curso_previo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'duracion': forms.TextInput(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'ubicacion-input',
                'list': 'sugerencias-ubicacion', 
            }),

            'latitud': forms.HiddenInput(attrs={'id': 'lat-input'}),
            'longitud': forms.HiddenInput(attrs={'id': 'lng-input'}),
            'foto': ClearableFileInput(attrs={'class': 'form-control'}),
            'categorias': forms.CheckboxSelectMultiple(),
            'curso_previo': forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
        }