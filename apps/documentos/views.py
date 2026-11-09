from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from .models import CategoriaDocumento, Documento


def lista(request):
    categorias = CategoriaDocumento.objects.all()
    qs = Documento.objects.filter(publicado=True)

    categoria_slug = request.GET.get("categoria")
    if categoria_slug:
        qs = qs.filter(categoria__slug=categoria_slug)

    buscar = request.GET.get("q")
    if buscar:
        qs = qs.filter(Q(titulo__icontains=buscar) | Q(descripcion__icontains=buscar))

    paginator = Paginator(qs, settings.PAGINACION_DOCUMENTOS)
    pagina = paginator.get_page(request.GET.get("page"))

    # Conserva búsqueda y categoría al cambiar de página.
    parametros = request.GET.copy()
    parametros.pop("page", None)

    contexto = {
        "querystring": parametros.urlencode(),
        "categorias": categorias,
        "documentos": pagina,
        "categoria_activa": categoria_slug,
        "buscar": buscar or "",
    }
    return render(request, "documentos/lista.html", contexto)
