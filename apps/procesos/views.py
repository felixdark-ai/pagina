from django.shortcuts import get_object_or_404, redirect, render

from .models import Proceso


def lista(request):
    contexto = {"procesos": Proceso.objects.filter(publicado=True)}
    return render(request, "procesos/lista.html", contexto)


def detalle(request, slug):
    proceso = get_object_or_404(Proceso, slug=slug, publicado=True, tipo=Proceso.TIPO_INTERNO)
    contexto = {
        "proceso": proceso,
        "etapas": proceso.lista_etapas(),
        "preguntas": proceso.lista_preguntas_frecuentes(),
        "plazos": proceso.lista_plazos(),
        "documentos": proceso.documentos_asociados.all(),
    }
    return render(request, "procesos/detalle.html", contexto)


def acceso(request, slug):
    """
    Página descriptiva para un sistema externo (POA, Desempeño Docente).
    El sistema externo administra su propio inicio de sesión.
    """
    proceso = get_object_or_404(Proceso, slug=slug, publicado=True, tipo=Proceso.TIPO_EXTERNO)
    return render(request, "procesos/acceso_externo.html", {"proceso": proceso})


def redirigir(request, slug):
    """Envía al usuario al sistema externo, que administra su propio acceso."""
    proceso = get_object_or_404(Proceso, slug=slug, publicado=True, tipo=Proceso.TIPO_EXTERNO)
    if not proceso.url_externa:
        return redirect("procesos:acceso", slug=proceso.slug)
    return redirect(proceso.url_externa)
