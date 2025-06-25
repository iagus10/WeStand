from django.db import models
from gestionLogin.models import User

class Publicacion(models.Model):
    """Publicaciones realizadas por los usuarios"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    imagen = models.ImageField(upload_to="publicaciones/", blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Publicación de {self.usuario.username} - {self.fecha_creacion.strftime('%d/%m/%Y')}"


class Comentario(models.Model):
    """Comentarios en publicaciones"""
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.publicacion.usuario.username}"


class MeGusta(models.Model):
    """Modelo para dar 'Me gusta' a publicaciones"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'publicacion')

    def __str__(self):
        return f"{self.usuario.username} le gusta {self.publicacion.usuario.username}"