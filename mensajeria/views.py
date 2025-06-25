from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from gestionLogin.models import Seguimiento
from .models import Conversacion, Mensaje
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string

User = get_user_model()

@login_required
def mensajes(request):
    conversaciones = Conversacion.objects.filter(participantes=request.user).order_by('-fecha_creacion')
    usuarios_seguidos = User.objects.filter(seguidores__seguidor=request.user) \
        .exclude(id=request.user.id) \
        .only('id', 'username', 'foto_perfil')[:20]
    usuarios_excluidos = list(usuarios_seguidos.values_list('id', flat=True)) + [request.user.id]
    usuarios_aleatorios = User.objects.exclude(id__in=usuarios_excluidos) \
        .only('id', 'username', 'foto_perfil') \
        .order_by('?')[:5]

    return render(request, 'mensajeria/mensajes.html', {
        'conversaciones': conversaciones,
        'usuarios_seguidos': usuarios_seguidos,
        'usuarios_aleatorios': usuarios_aleatorios,
    })

@login_required
def mensajes_conversacion(request, conversacion_id):
    conversacion = get_object_or_404(Conversacion, id=conversacion_id, participantes=request.user)
    offset = int(request.GET.get('offset', 0))
    cantidad = 5

    mensajes_qs = conversacion.mensajes.order_by('-fecha_envio')
    mensajes = mensajes_qs[offset:offset + cantidad]
    mensajes = list(mensajes)[::-1]  # Invertimos

    hay_mensajes = mensajes_qs.exists()

    return render(request, 'mensajeria/partials/mensajes_conversacion.html', {
        'conversacion': conversacion,
        'mensajes': mensajes,
        'hay_mensajes': hay_mensajes,
    })


@login_required
def crear_conversacion(request):
    if request.method == 'POST':
        usuario_ids = request.POST.getlist('usuarios')
        if usuario_ids:
            participantes = [request.user] + list(User.objects.filter(id__in=usuario_ids))

            posibles = Conversacion.objects.filter(participantes=request.user)
            for conversacion in posibles:
                if set(conversacion.participantes.all()) == set(participantes):
                    return JsonResponse({'success': False, 'error': 'Ya existe la conversación'})

            nombre_grupo = request.POST.get('nombre_grupo', '').strip()
            nueva_conversacion = Conversacion.objects.create(
                nombre_grupo=nombre_grupo if nombre_grupo else None
            )
            nueva_conversacion.participantes.add(*participantes)
            nueva_conversacion.save()

            # Ahora enviamos datos al JS
            es_grupo = len(participantes) > 2
            data = {
                'success': True,
                'conversacion_id': nueva_conversacion.id,
                'es_grupo': es_grupo,
            }

            if es_grupo:
                data['nombre_grupo'] = nueva_conversacion.nombre_grupo or "Grupo"
                data['fotos_participantes'] = [
                    p.foto_perfil.url if p.foto_perfil else None
                    for p in participantes if p != request.user
                ]
            else:
                otro = next((p for p in participantes if p != request.user), None)
                data['username_participante'] = otro.username if otro else ''
                data['foto_participante'] = otro.foto_perfil.url if (otro and otro.foto_perfil) else None

            return JsonResponse(data)

    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def buscar_usuarios(request):
    query = request.GET.get('q', '')
    usuarios = User.objects.filter(username__icontains=query).exclude(id=request.user.id)[:10]
    data = []
    for usuario in usuarios:
        data.append({
            'id': usuario.id,
            'username': usuario.username,
            'foto_perfil': usuario.foto_perfil.url if usuario.foto_perfil else None,
        })
    return JsonResponse(data, safe=False)

@login_required
def salir_conversacion(request, conversacion_id):
    conversacion = get_object_or_404(Conversacion, id=conversacion_id)

    if request.method == 'POST':
        if request.user in conversacion.participantes.all():
            conversacion.participantes.remove(request.user)

        if conversacion.participantes.count() == 0:
            conversacion.delete()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'ok': True})
        else:
            return redirect('mensajeria:mensajes')

    return redirect('mensajeria:mensajes')

@login_required
@csrf_exempt
def enviar_mensaje(request):
    if request.method == 'POST':
        conversacion_id = request.POST.get('conversacion_id')
        contenido = request.POST.get('contenido')

        conversacion = get_object_or_404(Conversacion, id=conversacion_id, participantes=request.user)

        mensaje = Mensaje.objects.create(
            conversacion=conversacion,
            remitente=request.user,
            contenido=contenido
        )

        return JsonResponse({
            'success': True,
            'mensaje_html': render_to_string('mensajeria/partials/mensaje.html', {'mensaje': mensaje, 'request': request})
        })

    return JsonResponse({'success': False})

@login_required
def contar_mensajes_no_leidos(request):
    no_leidos = Mensaje.objects.filter(destinatario=request.user, leido=False).count()
    return JsonResponse({'no_leidos': no_leidos})
