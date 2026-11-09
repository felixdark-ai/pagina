from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Noticia


def lista(request):
    qs = Noticia.objects.filter(publicado=True).prefetch_related("imagenes")
    paginator = Paginator(qs, settings.PAGINACION_NOTICIAS)
    pagina = paginator.get_page(request.GET.get("page"))
    return render(request, "noticias/lista.html", {"noticias": pagina})


def detalle(request, slug):
    noticia = get_object_or_404(Noticia.objects.prefetch_related("imagenes"), slug=slug, publicado=True)
    relacionadas = (
        Noticia.objects.filter(publicado=True).exclude(pk=noticia.pk).prefetch_related("imagenes")[:3]
    )
    portada = noticia.portada_url
    contexto = {
        "noticia": noticia,
        "galeria": noticia.imagenes.all(),
        "relacionadas": relacionadas,
        "og_imagen": request.build_absolute_uri(portada) if portada else "",
    }
    return render(request, "noticias/detalle.html", contexto)
