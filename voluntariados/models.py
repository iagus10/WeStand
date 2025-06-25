from django.db import models
from gestionLogin.models import User

class Voluntariado(models.Model):
    """Modelo de Voluntariado creado por entidades"""
    entidad = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'es_entidad': True})
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    duracion = models.CharField(max_length=50, blank=True, null=True)
    ubicacion = models.CharField(max_length=255)
    foto = models.ImageField(upload_to="voluntariados/", blank=True, null=True)
    categorias = models.ManyToManyField("gestionLogin.CategoriaVoluntariado")
    curso_previo = models.TextField(blank=True, null=True)
    finalizado = models.BooleanField(default=False)
    latitud = models.FloatField(blank=True, null=True)
    longitud = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class ParticipacionVoluntariado(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aceptado', 'Aceptado'),
        ('rechazado', 'Rechazado'),
        ('expulsado', 'Expulsados'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    voluntariado = models.ForeignKey(Voluntariado, on_delete=models.CASCADE)
    fecha_participacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    finalizado = models.BooleanField(default=False)
    

    def __str__(self):
        return f"{self.usuario.username} - {self.voluntariado.nombre} ({self.estado})"


class ValoracionVoluntariado(models.Model):
    """Valoraciones con estrellas sobre los voluntariados"""
    voluntariado = models.ForeignKey(Voluntariado, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="valoraciones_recibidas")
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="valoraciones_realizadas", null=False)
    estrellas = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.voluntariado.nombre} ({self.estrellas}⭐)"