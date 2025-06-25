from django.http import JsonResponse
from django.db.models import Q, Count
from gestionLogin.models import User
from publicaciones.models import Publicacion
from voluntariados.models import Voluntariado
from django.utils import timezone
import datetime


def buscar(request):
    query = request.GET.get('q', '').strip()
    resultados = {
        "usuarios": [],
        "publicaciones": [],
        "voluntariados": [],
        "busquedas_recientes": [],
    }

    # Búsquedas recientes desde sesión
    if not query:
        resultados["busquedas_recientes"] = request.session.get('busquedas_recientes', [])[:4]
        
        # Voluntariados recientes
        resultados["voluntariados"] = list(
            Voluntariado.objects.all().order_by('-fecha_inicio').values('id', 'nombre', 'entidad__username', 'entidad__foto_perfil')[:4]
        )

        # Publicaciones con más interacciones recientes (últimos 3 días)
        hace_3_dias = timezone.now() - datetime.timedelta(days=3)

        publicaciones = Publicacion.objects.annotate(
            num_likes=Count('megusta', filter=Q(megusta__fecha__gte=hace_3_dias)),
            num_comentarios=Count('comentario', filter=Q(comentario__fecha__gte=hace_3_dias))
        ).annotate(
            interacciones=Count('megusta', filter=Q(megusta__fecha__gte=hace_3_dias)) +
                          Count('comentario', filter=Q(comentario__fecha__gte=hace_3_dias))
        ).order_by('-interacciones', '-fecha_creacion')[:4]


        resultados["publicaciones"] = [
            {
                'id': p.id,
                'contenido': p.contenido,
                'usuario': p.usuario.username,
                'foto_perfil': p.usuario.foto_perfil.url if p.usuario.foto_perfil else ''
            } for p in publicaciones
        ]

    else:
        # Guardar búsqueda en sesión
        if request.GET.get('confirmar') == '1':
            busquedas = request.session.get('busquedas_recientes', [])
            if query not in busquedas:
                busquedas.insert(0, query)
            request.session['busquedas_recientes'] = busquedas[:10]

        # Buscar usuarios
        resultados["usuarios"] = list(User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(ubicacion__icontains=query)
        ).values('id', 'username', 'foto_perfil')[:5])

        # Buscar publicaciones
        resultados["publicaciones"] = list(Publicacion.objects.filter(
            contenido__icontains=query
        ).values('id', 'contenido')[:5])

        # Buscar voluntariados
        resultados["voluntariados"] = list(Voluntariado.objects.filter(
            nombre__icontains=query
        ).values('id', 'nombre', 'entidad__username')[:5])

    return JsonResponse(resultados)
