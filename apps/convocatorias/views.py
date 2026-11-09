from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import render

from .models import Convocatoria


def lista(request):
    qs = Convocatoria.objects.filter(publicado=True)
    paginator = Paginator(qs, settings.PAGINACION_CONVOCATORIAS)
    pagina = paginator.get_page(request.GET.get("page"))
    return render(request, "convocatorias/lista.html", {"convocatorias": pagina})
