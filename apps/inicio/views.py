from django.shortcuts import render

from apps.acreditacion.models import CarreraAcreditada
from apps.convocatorias.models import Convocatoria
from apps.documentos.models import Documento
from apps.noticias.models import Noticia
from apps.procesos.models import Proceso

from .models import HeroInicio, Indicador, SelloConfianza, Testimonio


def inicio(request):
    hero = HeroInicio.cargar()
    carreras = list(CarreraAcreditada.objects.filter(publicado=True))
    contexto = {
        "hero": hero,
        "hero_slides": hero.slides(),
        # Se muestran todos los procesos publicados, sean 3 o 10.
        "procesos": Proceso.objects.filter(publicado=True).order_by("orden", "titulo"),
        "sellos": SelloConfianza.objects.all(),
        "indicadores": Indicador.objects.filter(activo=True),
        "documentos_destacados": Documento.objects.filter(publicado=True, destacado=True)[:4],
        "noticias": Noticia.objects.filter(publicado=True).prefetch_related("imagenes")[:3],
        "convocatorias": Convocatoria.objects.filter(publicado=True, estado="abierta")[:3],
        "testimonios": Testimonio.objects.filter(publicado=True),
        "carreras_nacionales": [c for c in carreras if c.ambito == CarreraAcreditada.AMBITO_NACIONAL],
        "carreras_internacionales": [c for c in carreras if c.ambito == CarreraAcreditada.AMBITO_INTERNACIONAL],
    }
    return render(request, "inicio/inicio.html", contexto)
