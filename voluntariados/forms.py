from django import forms
from .models import ParticipacionVoluntariado

class ParticipacionVoluntariadoForm(forms.ModelForm):
    class Meta:
        model = ParticipacionVoluntariado
        fields = []
