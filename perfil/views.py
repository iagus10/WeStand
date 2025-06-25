from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import default_storage
from .models import Experiencia  
from gestionLogin.models import User, CategoriaVoluntariado, UsuarioPreferencia, Seguimiento, Habilidad, UsuarioHabilidad
from publicaciones.models import Publicacion, MeGusta
from voluntariados.models import Voluntariado, ValoracionVoluntariado
from publicaciones.models import Comentario
from perfil.forms import ExperienciaForm
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Avg
from insignias.models import UsuarioInsignia


@login_required
def perfil_view(request):
    user = request.user
    experiencias = Experiencia.objects.filter(usuario=user)
    categorias = CategoriaVoluntariado.objects.all()
    categorias_usuario = list(UsuarioPreferencia.objects.filter(usuario=user).values_list("categoria", flat=True))
    preferencias_usuario = UsuarioPreferencia.objects.filter(usuario=user).select_related("categoria")
    publicaciones = Publicacion.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    publicaciones_likes_usuario = MeGusta.objects.filter(usuario=request.user).values_list('publicacion_id', flat=True)
    entidades = User.objects.filter(user_type="organization")
    insignias_usuario = UsuarioInsignia.objects.filter(usuario=request.user).select_related("insignia")
    habilidades = Habilidad.objects.all()
    habilidades_usuario_ids = list(UsuarioHabilidad.objects.filter(usuario=user).values_list("habilidad_id", flat=True))

    if user.user_type == 'organization':
        valoraciones = ValoracionVoluntariado.objects.filter(
            voluntariado__entidad=user
        ).exclude(autor=user)
    else:
        valoraciones = ValoracionVoluntariado.objects.filter(
            usuario=user
        ).exclude(autor=user)

    media_valoraciones = valoraciones.aggregate(media=Avg("estrellas"))["media"]
    total_valoraciones = valoraciones.count()


    # Si es organización, obtener sus ofertas
    ofertas = None
    if user.user_type == 'organization':
        ofertas = Voluntariado.objects.filter(entidad=user).order_by('-fecha_inicio')

    if request.method == "POST":
        # Foto de perfil
        if "foto_perfil" in request.FILES:
            user.foto_perfil = request.FILES["foto_perfil"]
            user.save()
            messages.success(request, "Foto de perfil actualizada con éxito.")
            return redirect("perfil")

        elif "banner" in request.FILES:
            user.banner = request.FILES["banner"]
            user.save()
            messages.success(request, "Banner actualizado con éxito.")
            return redirect("perfil")

        elif "eliminar_foto" in request.POST:
            if user.foto_perfil:
                default_storage.delete(user.foto_perfil.path)
                user.foto_perfil = None
                user.save()
                messages.success(request, "Foto de perfil eliminada con éxito.")
            return redirect("perfil")

        elif "eliminar_banner" in request.POST:
            if user.banner:
                default_storage.delete(user.banner.path)
                user.banner = None
                user.save()
                messages.success(request, "Banner eliminado con éxito.")
            return redirect("perfil")
        
        elif "guardar_perfil" in request.POST:
            user.biografia = request.POST.get("biografia", user.biografia)
            user.ubicacion = request.POST.get("ubicacion", user.ubicacion)
            user.disponibilidad = request.POST.get("disponibilidad", user.disponibilidad)

            categorias_seleccionadas = request.POST.getlist('categorias_voluntariado')
            UsuarioPreferencia.objects.filter(usuario=user).delete()
            nuevas_preferencias = [UsuarioPreferencia(usuario=user, categoria_id=c) for c in categorias_seleccionadas]
            UsuarioPreferencia.objects.bulk_create(nuevas_preferencias)

            user.save()
            messages.success(request, "Perfil actualizado con éxito.")
            return redirect("perfil")

        
        elif "guardar_habilidades" in request.POST:
            habilidades_seleccionadas = request.POST.getlist('habilidades')
            UsuarioHabilidad.objects.filter(usuario=user).delete()
            nuevas_habilidades = [UsuarioHabilidad(usuario=user, habilidad_id=h) for h in habilidades_seleccionadas]
            UsuarioHabilidad.objects.bulk_create(nuevas_habilidades)
            messages.success(request, "Habilidades actualizadas con éxito.")
            return redirect("perfil")
    
    return render(request, "perfil/perfil.html", {
        "user": user,
        "experiencias": experiencias,
        "categorias": categorias,
        "categorias_usuario": categorias_usuario,
        "preferencias_usuario": preferencias_usuario,
        "entidades": entidades,
        "publicaciones": publicaciones,
        "publicaciones_likes_usuario": publicaciones_likes_usuario,
        "ofertas": ofertas, 
        "valoraciones": valoraciones, 
        "media_valoraciones": media_valoraciones,
        "total_valoraciones": total_valoraciones,
        'insignias_usuario': insignias_usuario,
        'habilidades': habilidades,
        'habilidades_usuario_ids': habilidades_usuario_ids,
    })



@login_required

def agregar_experiencia(request):
    form = ExperienciaForm()

    if request.method == "POST":
        form = ExperienciaForm(request.POST)
        if form.is_valid():
            experiencia = form.save(commit=False)
            experiencia.usuario = request.user
            experiencia.save()
            return redirect('perfil')

    return render(request, 'perfil/agregar_experiencia.html', {
        'form': form,
 
    })

@login_required
def editar_experiencia(request, experiencia_id):
    experiencia = get_object_or_404(Experiencia, id=experiencia_id, usuario=request.user)

    if request.method == "POST":
        form = ExperienciaForm(request.POST, instance=experiencia)
        if form.is_valid():
            form.save()
            return redirect("perfil")
    else:
        form = ExperienciaForm(instance=experiencia)

    return render(request, "perfil/agregar_experiencia.html", {
        "form": form,
        "modo_edicion": True,  
    })

def eliminar_experiencia(request, id):
    experiencia = get_object_or_404(Experiencia, id=id, usuario=request.user)

    if request.method == 'POST':
        experiencia.delete()
        messages.success(request, 'Experiencia eliminada correctamente.')
        return redirect('perfil')

    messages.error(request, 'Acción no permitida.')
    return redirect('perfil')


@login_required
def ver_perfil(request, username):
    perfil = get_object_or_404(User, username=username)
    es_organizacion = perfil.user_type == 'organization'
    publicaciones_likes_usuario = MeGusta.objects.filter(usuario=request.user).values_list('publicacion_id', flat=True)
    preferencias_usuario = UsuarioPreferencia.objects.filter(usuario=perfil)
    entidades = User.objects.filter(user_type="organization")
    insignias_usuario = UsuarioInsignia.objects.filter(usuario=perfil).select_related('insignia')
    habilidades_usuario = UsuarioHabilidad.objects.filter(usuario=perfil).select_related("habilidad")



    if es_organizacion:
        valoraciones = ValoracionVoluntariado.objects.filter(
            voluntariado__entidad=perfil
        ).exclude(autor=perfil).select_related("autor", "voluntariado").order_by('-fecha')
    else:
        valoraciones = ValoracionVoluntariado.objects.filter(
            usuario=perfil
        ).exclude(autor=perfil).select_related("autor", "voluntariado").order_by('-fecha')

    media_valoraciones = valoraciones.aggregate(media=Avg("estrellas"))["media"]
    total_valoraciones = valoraciones.count()
    publicaciones = Publicacion.objects.filter(usuario=perfil).order_by('-fecha_creacion')
    ofertas = Voluntariado.objects.filter(entidad=perfil).order_by('-fecha_inicio') if es_organizacion else None
    experiencias = Experiencia.objects.filter(usuario=perfil).order_by('-fecha_inicio') if not es_organizacion else None

    ya_sigo = Seguimiento.objects.filter(seguidor=request.user, seguido=perfil).exists()
    seguidores = Seguimiento.objects.filter(seguido=perfil).count()
    siguiendo = Seguimiento.objects.filter(seguidor=perfil).count()

    context = {
        'perfil': perfil,
        'es_organizacion': es_organizacion,
        'publicaciones': publicaciones,
        'ofertas': ofertas,
        'experiencias': experiencias,
        'ya_sigo': ya_sigo,
        'seguidores': seguidores,
        'siguiendo': siguiendo,
        'preferencias_usuario': preferencias_usuario,
        'publicaciones_likes_usuario': publicaciones_likes_usuario,
        'entidades': entidades,
        'valoraciones': valoraciones,
        "media_valoraciones": media_valoraciones,
        "total_valoraciones": total_valoraciones,
        'insignias_usuario': insignias_usuario,
        'habilidades_usuario': habilidades_usuario,

    }

    return render(request, 'perfil/visitar_perfil.html', context)


@login_required
def toggle_seguimiento(request, username):
    seguido = get_object_or_404(User, username=username)
    if seguido == request.user:
        return JsonResponse({'ok': False, 'error': 'No puedes seguirte a ti mismo'}, status=400)

    seguimiento, creado = Seguimiento.objects.get_or_create(seguidor=request.user, seguido=seguido)

    if not creado:
        seguimiento.delete()
        siguiendo = False
    else:
        siguiendo = True

    total_seguidores = Seguimiento.objects.filter(seguido=seguido).count()

    return JsonResponse({
        'ok': True,
        'siguiendo': siguiendo,
        'total_seguidores': total_seguidores
    })

@require_POST
@login_required
def eliminar_comentario(request, id):
    comentario = get_object_or_404(Comentario, id=id)

    if comentario.usuario == request.user or comentario.publicacion.usuario == request.user:
        comentario.delete()
        return JsonResponse({'ok': True})
    
    return JsonResponse({'ok': False, 'error': 'No autorizado'}, status=403)

@require_POST
@login_required
def eliminar_oferta(request, id):
    oferta = get_object_or_404(Voluntariado, id=id, entidad=request.user)

    oferta.delete()
    return JsonResponse({'ok': True})


