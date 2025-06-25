# notificaciones/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from notificaciones.models import Notificacion
from publicaciones.models import Comentario, MeGusta
from gestionLogin.models import Seguimiento
from voluntariados.models import Voluntariado

# Notificación por comentario
@receiver(post_save, sender=Comentario)
def notificar_comentario(sender, instance, created, **kwargs):
    if created:
        publicacion = instance.publicacion
        autor_publicacion = publicacion.usuario
        comentarista = instance.usuario

        if autor_publicacion != comentarista:
            comentario_texto = instance.contenido.strip()
            comentario_resumen = comentario_texto[:100] + "..." if len(comentario_texto) > 100 else comentario_texto

            Notificacion.objects.create(
                usuario=autor_publicacion,
                actor=comentarista,
                tipo='comentario',
                mensaje=f"{comentarista.username} comentó: \"{comentario_resumen}\"",
                publicacion=publicacion  # ⚡ Ahora se guarda también la publicación
            )

# Notificación por me gusta
@receiver(post_save, sender=MeGusta)
def notificar_me_gusta(sender, instance, created, **kwargs):
    if created:
        autor_publicacion = instance.publicacion.usuario
        actor = instance.usuario
        if autor_publicacion != actor:
            Notificacion.objects.create(
                usuario=autor_publicacion,
                actor=actor,
                tipo='me_gusta',
                mensaje=f"{actor.username} le ha dado me gusta a tu publicación.",
                publicacion=instance.publicacion  # ⚡ También guardamos la publicación
            )

# Notificación por follow
@receiver(post_save, sender=Seguimiento)
def notificar_follow(sender, instance, created, **kwargs):
    if created:
        seguido = instance.seguido
        seguidor = instance.seguidor
        if seguido != seguidor:
            Notificacion.objects.create(
                usuario=seguido,
                actor=seguidor,
                tipo='follow',
                mensaje=f"{seguidor.username} ha comenzado a seguirte."
            )


@receiver(post_save, sender=Voluntariado)
def notificar_nuevo_voluntariado(sender, instance, created, **kwargs):
    if created:
        entidad = instance.entidad
        seguidores = Seguimiento.objects.filter(seguido=entidad).select_related('seguidor')

        for seguimiento in seguidores:
            Notificacion.objects.create(
                usuario=seguimiento.seguidor,
                actor=entidad,
                tipo='voluntariado',  # Muy importante: igual que en tu modelo
                mensaje=f"{entidad.username} ha publicado una nueva oferta de voluntariado.",
                voluntariado=instance  # ← Ahora se puede guardar el objeto
            )