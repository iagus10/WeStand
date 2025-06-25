from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PublicacionForm, VoluntariadoForm
from .models import Publicacion, MeGusta, Comentario
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from voluntariados.models import Voluntariado
from datetime import datetime
from django.contrib import messages
from gestionLogin.models import Seguimiento, UsuarioPreferencia, User, UsuarioHabilidad
from django.db.models import Count


@login_required
def index(request):
    user = request.user
    publicaciones = Publicacion.objects.all().order_by('-fecha_creacion')
    ofertas = Voluntariado.objects.all().order_by('-fecha_inicio')
    publicaciones_liked_usuario = MeGusta.objects.filter(usuario=user).values_list('publicacion_id', flat=True)
    es_entidad = user.user_type == 'organization'

    pub_form = PublicacionForm()
    oferta_form = VoluntariadoForm() if es_entidad else None
    formulario_activo = 'publicacion'

    # Lógica de sugerencias
    ya_sigo_ids = Seguimiento.objects.filter(seguidor=user).values_list('seguido_id', flat=True)
    seguidores_mios = Seguimiento.objects.filter(seguidor=user).values_list('seguido_id', flat=True)

    sugerencias_seguidores = User.objects.exclude(id__in=ya_sigo_ids).exclude(id=user.id).filter(
        id__in=Seguimiento.objects.filter(seguidor__in=seguidores_mios).values_list("seguido_id", flat=True)
    ).annotate(num_comunes=Count('id')).order_by('-num_comunes')[:5]

    mis_categorias = UsuarioPreferencia.objects.filter(usuario=user).values_list('categoria_id', flat=True)
    sugerencias_intereses = User.objects.exclude(id__in=ya_sigo_ids).exclude(id=user.id).filter(
        id__in=UsuarioPreferencia.objects.filter(categoria_id__in=mis_categorias).values_list("usuario_id", flat=True)
    ).distinct()[:5]

    mis_habilidades = UsuarioHabilidad.objects.filter(usuario=user).values_list('habilidad_id', flat=True)
    sugerencias_habilidades = User.objects.exclude(id__in=ya_sigo_ids).exclude(id=user.id).filter(
        id__in=UsuarioHabilidad.objects.filter(habilidad_id__in=mis_habilidades).values_list("usuario_id", flat=True)
    ).distinct()[:5]

    sugerencias = list(set(sugerencias_seguidores) | set(sugerencias_intereses) | set(sugerencias_habilidades))

    # Procesamiento de formularios
    if request.method == 'POST':
        if 'submit_post' in request.POST:
            pub_form = PublicacionForm(request.POST, request.FILES)
            if pub_form.is_valid():
                nueva_pub = pub_form.save(commit=False)
                nueva_pub.usuario = user
                nueva_pub.save()
                return redirect('index')
            else:
                formulario_activo = 'publicacion'

        elif 'submit_oferta' in request.POST and es_entidad:
            oferta_form = VoluntariadoForm(request.POST, request.FILES)
            if oferta_form.is_valid():
                nueva_oferta = oferta_form.save(commit=False)

                if not nueva_oferta.latitud or not nueva_oferta.longitud:
                    messages.error(request, "Debes seleccionar una ubicación válida de la lista.")
                    formulario_activo = 'voluntariado'
                else:
                    nueva_oferta.entidad = user
                    nueva_oferta.save()
                    oferta_form.save_m2m()
                    return redirect('index')
            else:
                formulario_activo = 'voluntariado'

    return render(request, 'index.html', {
        'pub_form': pub_form,
        'oferta_form': oferta_form,
        'publicaciones': publicaciones,
        'ofertas': ofertas,
        'publicaciones_liked_usuario': publicaciones_liked_usuario,
        'es_entidad': es_entidad,
        'formulario_activo': formulario_activo,
        'sugerencias': sugerencias, 
    })


@require_POST
@login_required
def toggle_like(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)
    like, created = MeGusta.objects.get_or_create(usuario=request.user, publicacion=publicacion)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    total_likes = MeGusta.objects.filter(publicacion=publicacion).count()
    return JsonResponse({'liked': liked, 'total_likes': total_likes})



@login_required
def comentar_publicacion(request, pk):
    if request.method == "POST":
        data = json.loads(request.body)
        contenido = data.get("contenido")

        publicacion = get_object_or_404(Publicacion, pk=pk)
        nuevo_comentario = Comentario.objects.create(
            publicacion=publicacion,
            usuario=request.user,
            contenido=contenido
        )

        foto_url = request.user.foto_perfil.url if request.user.foto_perfil else None

        return JsonResponse({
            "ok": True,
            "id": nuevo_comentario.id,
            "contenido": nuevo_comentario.contenido,
            "usuario": request.user.username,
            "comentarios": publicacion.comentario_set.count(),
            "foto_url": foto_url,
            "fecha": nuevo_comentario.fecha.isoformat()  # Esto es lo importante para usar con Day.js
        })

    return JsonResponse({"ok": False}, status=400)

@login_required
def eliminar_publicacion(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk, usuario=request.user)
    publicacion.delete()
    return redirect('index')

@require_POST
@login_required
def eliminar_comentario(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)

    if comentario.usuario == request.user or comentario.publicacion.usuario == request.user:
        comentario.delete()
        return JsonResponse({"ok": True})
    
    return JsonResponse({"ok": False}, status=403)


@require_POST
@login_required
def eliminar_oferta_voluntariado(request, id):
    oferta = get_object_or_404(Voluntariado, id=id, entidad=request.user)
    oferta.delete()
    return JsonResponse({'ok': True})