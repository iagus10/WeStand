from django.db import models
from django.conf import settings

class Experiencia(models.Model):
    """Modelo para almacenar experiencias de los usuarios en voluntariados"""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="experiencias")
    titulo = models.CharField(max_length=255)  # Nombre de la experiencia
    organizacion = models.CharField(max_length=255, blank=True, null=True)  # Organización relacionada
    descripcion = models.TextField(blank=True, null=True)  # Descripción de la experiencia
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)  # Puede estar en curso

    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"