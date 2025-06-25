from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):  
    """Modelo extendido para usuarios (voluntarios y organizaciones)"""
    
    USER_TYPES = [
        ('volunteer', 'Voluntario'),
        ('organization', 'Organización')
    ]
    
    user_type = models.CharField(max_length=15, choices=USER_TYPES)  # Tipo de usuario
    email = models.EmailField(unique=True)  # Email único
    foto_perfil = models.ImageField(upload_to="perfiles/", blank=True, null=True)  
    biografia = models.TextField(blank=True, null=True)
    banner = models.ImageField(upload_to='banners/', null=True, blank=True)  
    ubicacion = models.CharField(max_length=100, blank=True, null=True)  
    disponibilidad = models.CharField(max_length=100, blank=True, null=True)  
    nivel = models.IntegerField(default=1)  
    experiencia = models.IntegerField(default=0)  

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class CategoriaVoluntariado(models.Model):
    """Categorías de voluntariado disponibles"""
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class UsuarioPreferencia(models.Model):
    """Relación entre usuarios y sus intereses en voluntariados"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.ForeignKey(CategoriaVoluntariado, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.usuario.username} - {self.categoria.nombre}"


class Habilidad(models.Model):
    """Habilidades disponibles para que los usuarios las seleccionen"""
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class UsuarioHabilidad(models.Model):
    """Relación entre usuarios y sus habilidades"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    habilidad = models.ForeignKey(Habilidad, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.usuario.username} - {self.habilidad.nombre}"


class Seguimiento(models.Model):
    """Modelo para permitir que los usuarios se sigan entre sí"""
    seguidor = models.ForeignKey(User, related_name="siguiendo", on_delete=models.CASCADE)
    seguido = models.ForeignKey(User, related_name="seguidores", on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('seguidor', 'seguido')

    def __str__(self):
        return f"{self.seguidor.username} sigue a {self.seguido.username}"
