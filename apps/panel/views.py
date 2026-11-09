from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render

from apps.contacto.models import MensajeContacto
from apps.convocatorias.models import Convocatoria
from apps.documentos.models import Documento
from apps.noticias.models import Noticia


def es_staff(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(es_staff)
def inicio(request):
    contexto = {
        "total_documentos": Documento.objects.count(),
        "total_noticias": Noticia.objects.count(),
        "total_convocatorias": Convocatoria.objects.count(),
        "mensajes_pendientes": MensajeContacto.objects.filter(atendido=False).count(),
    }
    return render(request, "panel/inicio.html", contexto)
