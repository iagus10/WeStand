from django import forms
from gestionLogin.models import User
from perfil.models import Experiencia

class PerfilForm(forms.ModelForm):
    """Formulario para editar el perfil del usuario."""
    
    class Meta:
        model = User
        fields = ['foto_perfil', 'biografia', 'ubicacion', 'disponibilidad', 'user_type']
        widgets = {
            'biografia': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'disponibilidad': forms.TextInput(attrs={'class': 'form-control'}),
            
        }


class ExperienciaForm(forms.ModelForm):
    organizacion = forms.CharField(widget=forms.Select(), required=False)

    class Meta:
        model = Experiencia
        fields = ['titulo', 'organizacion', 'descripcion', 'fecha_inicio', 'fecha_fin']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        entidades = User.objects.filter(user_type='organization').values_list('username', flat=True)
        choices = [(entidad, entidad) for entidad in entidades]
        self.fields['organizacion'].widget.attrs.update({
            'class': 'form-select select2-org',
        })
        self.fields['organizacion'].widget.choices = choices