from django.db import models
from django.conf import settings
from django.utils.timezone import now

class Conversacion(models.Model):
    participantes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="conversaciones")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    nombre_grupo = models.CharField(max_length=255, blank=True, null=True)  # <-- NUEVO

    def __str__(self):
        if self.nombre_grupo:
            return f"Grupo: {self.nombre_grupo}"
        return f"Conversación {self.id}"

class Mensaje(models.Model):
    """Representa un mensaje dentro de una conversación."""
    conversacion = models.ForeignKey(Conversacion, on_delete=models.CASCADE, related_name="mensajes")
    remitente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mensajes_enviados")
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(default=now)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"De {self.remitente.username} en Conversación {self.conversacion.id}"

    class Meta:
        ordering = ['fecha_envio']
