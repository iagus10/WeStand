# notificaciones/models.py
from django.db import models
from django.conf import settings
from django.utils.timezone import now

class Notificacion(models.Model):
    TIPO_CHOICES = [
        ('mensaje', 'Mensaje nuevo'),
        ('voluntariado', 'Nueva oferta de voluntariado'),
        ('comentario', 'Nuevo comentario en tu publicación'),
        ('me_gusta', 'Me gusta en tu publicación'),
        ('insignia', 'Nueva insignia obtenida'),
        ('follow', 'Nuevo seguidor'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificaciones"
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="acciones",
        null=True,
        blank=True
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(default=now)
    leido = models.BooleanField(default=False)
    
    publicacion = models.ForeignKey(
        'publicaciones.Publicacion',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notificaciones'
    )

    voluntariado = models.ForeignKey(
        'voluntariados.Voluntariado',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notificaciones_voluntariado'
    )

    def __str__(self):
        return f"Notificación ({self.tipo}) para {self.usuario}"

    class Meta:
        ordering = ['-fecha_creacion']
