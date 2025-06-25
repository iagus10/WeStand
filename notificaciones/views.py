from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Notificacion
from django.db.models.signals import post_save
from gestionLogin.models import Seguimiento
from django.dispatch import receiver
from voluntariados.models import Voluntariado
from django.urls import reverse
from publicaciones.models import Comentario

@login_required
def obtener_notificaciones(request):
    notifs = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_creacion')[:10]
    data = []
    for notif in notifs:
        actor = notif.actor
        foto = None
        if actor:
            if hasattr(actor, 'foto_perfil') and actor.foto_perfil:
                foto = actor.foto_perfil.url
            else:
                foto = None  # Mostrará icono Bootstrap en frontend si no hay foto

        url = "#"
        publicacion_id = None

        if notif.tipo in ["comentario", "me_gusta"]:
            if notif.publicacion:
                publicacion_id = notif.publicacion.id
                url = reverse('perfil') + f"?publicacion_id={publicacion_id}&tipo_notificacion={notif.tipo}"
            else:
                url = reverse('perfil')

        elif notif.tipo == "follow" and actor:
            url = reverse('visitar_perfil', args=[actor.username])

        elif notif.tipo == "voluntariado":
            if notif.voluntariado:
                # Si es una notificación para la entidad (alguien se ha inscrito)
                if notif.usuario == notif.voluntariado.entidad:
                    url = reverse("ver_solicitudes", args=[notif.voluntariado.id])
                else:
                    # Es una notificación para un voluntario
                    participacion = notif.voluntariado.participacionvoluntariado_set.filter(
                        usuario=request.user
                    ).first()

                    if participacion:
                        if participacion.estado == 'aceptado':
                            url = reverse('voluntariado_aceptado', args=[notif.voluntariado.id])
                        elif participacion.estado == 'rechazado':
                            url = reverse('inscripcion_voluntariado', args=[notif.voluntariado.id])  # Sin enlace si fue rechazado
                        else:
                            url = reverse('inscripcion_voluntariado', args=[notif.voluntariado.id])
                    else:
                        # Aún no se ha inscrito → mostrar enlace a inscripción
                        url = reverse('inscripcion_voluntariado', args=[notif.voluntariado.id])


        data.append({
            'actor': actor.username if actor else 'Sistema',
            'foto_perfil': foto,
            'mensaje': notif.mensaje,
            'tipo': notif.tipo,
            'leido': notif.leido,
            'fecha': notif.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
            'url': url,
            'publicacion_id': publicacion_id,
        })

    return JsonResponse({'notificaciones': data})

@login_required
def contar_no_leidas(request):
    total = Notificacion.objects.filter(usuario=request.user, leido=False).count()
    return JsonResponse({'no_leidas': total})

@login_required
def marcar_notificaciones_leidas(request):
    Notificacion.objects.filter(usuario=request.user, leido=False).update(leido=True)
    return JsonResponse({'success': True})

