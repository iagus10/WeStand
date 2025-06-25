from django.db import models
from gestionLogin.models import User

class Insignia(models.Model):
    """Insignias otorgadas a los usuarios por sus logros"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    icono = models.ImageField(upload_to="insignias/")

    def __str__(self):
        return self.nombre


class UsuarioInsignia(models.Model):
    """Relación entre usuarios e insignias obtenidas"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    insignia = models.ForeignKey(Insignia, on_delete=models.CASCADE)
    fecha_otorgada = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.insignia.nombre}"