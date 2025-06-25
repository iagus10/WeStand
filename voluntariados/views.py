from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import Voluntariado, ParticipacionVoluntariado, ValoracionVoluntariado
from notificaciones.models import Notificacion
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.db.models import Avg
from django.views.decorators.http import require_POST
from insignias.utils import aumentar_experiencia_y_nivel

#from insignias.utils import aumentar_nivel_si_corresponde

@login_required
def inscripcion_voluntariado(request, voluntariado_id):
    voluntariado = get_object_or_404(Voluntariado, pk=voluntariado_id)

    if request.user.user_type != 'volunteer':
        return redirect('index')

    participacion = ParticipacionVoluntariado.objects.filter(
        usuario=request.user, voluntariado=voluntariado
    ).first()

    estado = participacion.estado if participacion else None

    # Si el voluntariado ha finalizado, no permitir ni mostrar botón de inscripción
    if voluntariado.finalizado:
        return render(request, 'voluntariados/inscripcion_voluntariado.html', {
            'voluntariado': voluntariado,
            'estado': estado,
            'finalizado': True
        })

    if request.method == 'POST':
        if not participacion:
            ParticipacionVoluntariado.objects.create(
                usuario=request.user, voluntariado=voluntariado
            )
            Notificacion.objects.create(
                usuario=voluntariado.entidad,
                actor=request.user,
                tipo='voluntariado',
                mensaje=f"{request.user.username} ha solicitado participar en \"{voluntariado.nombre}\".",
                voluntariado=voluntariado
            )
        return redirect('inscripcion_voluntariado', voluntariado_id=voluntariado.id)

    return render(request, 'voluntariados/inscripcion_voluntariado.html', {
        'voluntariado': voluntariado,
        'estado': estado,
        'finalizado': False
    })


@login_required
def ver_solicitudes(request, voluntariado_id):
    oferta = get_object_or_404(Voluntariado, id=voluntariado_id, entidad=request.user)

    pendientes = ParticipacionVoluntariado.objects.filter(voluntariado=oferta, estado='pendiente')
    aceptadas = ParticipacionVoluntariado.objects.filter(voluntariado=oferta, estado='aceptado')
    rechazadas = ParticipacionVoluntariado.objects.filter(voluntariado=oferta, estado='rechazado')
    expulsados = ParticipacionVoluntariado.objects.filter(voluntariado=oferta, estado='expulsado')

    # Valoraciones que los voluntarios han hecho al voluntariado
    valoraciones_recibidas = ValoracionVoluntariado.objects.filter(
        voluntariado=oferta
    ).exclude(autor=request.user).select_related("autor")

    # Valoraciones que esta entidad ha hecho a los voluntarios
    valoraciones_hechas = ValoracionVoluntariado.objects.filter(
        voluntariado=oferta,
        autor=request.user
    ).select_related("usuario")

    valoraciones_dict = {v.usuario_id: v for v in valoraciones_hechas}
    media_estrellas = valoraciones_recibidas.aggregate(promedio=Avg('estrellas'))['promedio']

    context = {
        'oferta': oferta,
        'agrupadas': [
            ('Pendientes', pendientes),
            ('Aceptadas', aceptadas),
            ('Rechazadas', rechazadas),
            ('Expulsados', expulsados)
        ],
        'valoraciones_dict': valoraciones_dict,  # las que tú (entidad) has hecho
        'valoraciones_recibidas': valoraciones_recibidas,  # las que te han hecho los voluntarios
        'media_estrellas': media_estrellas,
    }

    return render(request, 'voluntariados/ver_solicitudes.html', context)



@login_required
def gestionar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(ParticipacionVoluntariado, id=solicitud_id)

    if request.method == "POST":
        accion = request.POST.get("accion")
        if accion == "aceptar":
            solicitud.estado = "aceptado"
            mensaje = f"Has sido aceptado en la oferta \"{solicitud.voluntariado.nombre}\"."
            
        elif accion == "rechazar":
            solicitud.estado = "rechazado"
            mensaje = f"Has sido rechazado en la oferta \"{solicitud.voluntariado.nombre}\"."
            

        solicitud.save()

        # Crear notificación al usuario solicitante
        Notificacion.objects.create(
            usuario=solicitud.usuario,
            actor=request.user,
            tipo="voluntariado",
            mensaje=mensaje,
            voluntariado=solicitud.voluntariado
        )

        return redirect("ver_solicitudes", voluntariado_id=solicitud.voluntariado.id)
    
@login_required
def voluntariado_aceptado(request, voluntariado_id):
    voluntariado = get_object_or_404(Voluntariado, id=voluntariado_id)

    # Comprobar si el usuario está aceptado en este voluntariado
    participacion = ParticipacionVoluntariado.objects.filter(
        usuario=request.user,
        voluntariado=voluntariado,
        estado='aceptado'
    ).first()

    if not participacion:
        raise PermissionDenied("No tienes acceso a esta información.")

    participantes = ParticipacionVoluntariado.objects.filter(
        voluntariado=voluntariado,
        estado='aceptado'
    ).select_related('usuario')

    ha_valorado = ValoracionVoluntariado.objects.filter(
        voluntariado=voluntariado,
        usuario=request.user,
        autor=request.user
    ).exists()

    valoracion = ValoracionVoluntariado.objects.filter(
        voluntariado=voluntariado,
        usuario=request.user,
        autor=request.user
    ).first()


    return render(request, 'voluntariados/voluntariado_aceptado.html', {
        'voluntariado': voluntariado,
        'participantes': participantes,
        'participacion': participacion,
        'ha_valorado': bool(valoracion),
        'valoracion': valoracion,
        'rango_estrellas': range(1, 6),
    })

@login_required
def finalizar_participacion(request, participacion_id):
    participacion = get_object_or_404(ParticipacionVoluntariado, id=participacion_id)

    if request.user != participacion.voluntariado.entidad:
        return HttpResponseForbidden("No tienes permiso para finalizar esta participación.")

    # Solo finalizar si está aceptado y no finalizado
    if participacion.estado == "aceptado" and not participacion.finalizado:
        participacion.finalizado = True
        participacion.save()

        aumentar_experiencia_y_nivel(participacion.usuario)

    return redirect("ver_solicitudes", voluntariado_id=participacion.voluntariado.id)

@login_required
def finalizar_voluntariado(request, voluntariado_id):
    voluntariado = get_object_or_404(Voluntariado, id=voluntariado_id)

    if request.user != voluntariado.entidad:
        raise PermissionDenied("No tienes permiso para finalizar este voluntariado.")

    if request.method == "POST" and not voluntariado.finalizado:
        participaciones = ParticipacionVoluntariado.objects.filter(
            voluntariado=voluntariado, estado='aceptado', finalizado=False
        )

        for p in participaciones:
            p.finalizado = True
            p.save()
            aumentar_experiencia_y_nivel(p.usuario)
            # Notificación al participante
            Notificacion.objects.create(
                usuario=p.usuario,
                actor=voluntariado.entidad,
                tipo='voluntariado',
                mensaje=f"El voluntariado \"{voluntariado.nombre}\" ha finalizado. ¡Gracias por tu participación!",
                voluntariado=voluntariado
            )

        voluntariado.finalizado = True
        voluntariado.save()

    return redirect('ver_solicitudes', voluntariado_id=voluntariado.id)

@login_required
def expulsar_participante(request, participacion_id):
    participacion = get_object_or_404(ParticipacionVoluntariado, id=participacion_id)

    if request.user != participacion.voluntariado.entidad:
        return HttpResponseForbidden("No tienes permiso para expulsar a este participante.")

    if participacion.estado == "aceptado" and not participacion.finalizado:
        participacion.estado = "expulsado"
        participacion.save()

        # Notificación al voluntario expulsado
        Notificacion.objects.create(
            usuario=participacion.usuario,
            actor=request.user,
            tipo="voluntariado",
            mensaje=f"Has sido expulsado del voluntariado \"{participacion.voluntariado.nombre}\".",
            voluntariado=participacion.voluntariado
        )

    return redirect("ver_solicitudes", voluntariado_id=participacion.voluntariado.id)

@login_required
def readmitir_participante(request, participacion_id):
    
    participacion = get_object_or_404(ParticipacionVoluntariado, id=participacion_id)

    if request.user != participacion.voluntariado.entidad:
        return HttpResponseForbidden("No tienes permiso para expulsar a este participante.")
    
    if request.method == "POST":
        participacion.estado = "aceptado"
        participacion.save()

        Notificacion.objects.create(
            usuario=participacion.usuario,
            actor=request.user,
            tipo="voluntariado",
            mensaje=f"Has sido readmitido en el voluntariado \"{participacion.voluntariado.nombre}\".",
            voluntariado=participacion.voluntariado
        )

    return redirect("ver_solicitudes", voluntariado_id=participacion.voluntariado.id)


@login_required
def valorar_voluntariado(request, voluntariado_id):
    voluntariado = get_object_or_404(Voluntariado, id=voluntariado_id)
    participacion = get_object_or_404(
        ParticipacionVoluntariado,
        voluntariado=voluntariado,
        usuario=request.user,
        estado='aceptado',
        finalizado=True
    )

    ya_valorado = ValoracionVoluntariado.objects.filter(
        voluntariado=voluntariado,
        usuario=request.user,
        autor=request.user
    ).exists()

    if request.method == "POST" and not ya_valorado:
        estrellas = request.POST.get("estrellas")
        comentario = request.POST.get("comentario", "").strip()

        ValoracionVoluntariado.objects.create(
            voluntariado=voluntariado,
            usuario=request.user,  # el voluntario
            autor=request.user,    # el que valora (el mismo)
            estrellas=int(estrellas),
            comentario=comentario if comentario else None
        )

    return redirect("voluntariado_aceptado", voluntariado_id=voluntariado.id)


@login_required
@require_POST
def valorar_voluntario(request, participacion_id):
    participacion = get_object_or_404(
        ParticipacionVoluntariado,
        id=participacion_id,
        voluntariado__entidad=request.user  # asegura que la entidad es la dueña del voluntariado
    )

    if not participacion.finalizado:
        messages.error(request, "Solo puedes valorar a participantes que han finalizado su participación.")
        return redirect('ver_solicitudes', participacion.voluntariado.id)

    ya_valorado = ValoracionVoluntariado.objects.filter(
        voluntariado=participacion.voluntariado,
        usuario=participacion.usuario,
        autor=request.user  # ← esto es lo importante
    ).exists()

    if ya_valorado:
        messages.warning(request, "Ya has valorado a este voluntario.")
        return redirect('ver_solicitudes', participacion.voluntariado.id)

    estrellas = request.POST.get("estrellas")
    comentario = request.POST.get("comentario", "").strip()

    if estrellas:
        ValoracionVoluntariado.objects.create(
            voluntariado=participacion.voluntariado,
            usuario=participacion.usuario,  # voluntario
            autor=request.user,             # entidad que valora
            estrellas=int(estrellas),
            comentario=comentario if comentario else None
        )
        messages.success(request, "Valoración registrada con éxito.")

    else: 
        messages.error(request, "Debe puntuar antes de valorar!")

    return redirect("ver_solicitudes", participacion.voluntariado.id)
