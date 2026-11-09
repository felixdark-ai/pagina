from django.shortcuts import get_object_or_404, render

from .models import CarreraAcreditada


def detalle(request, slug):
    """
    Detalle público de la acreditación de una carrera. Solo se muestran los
    campos explícitamente marcados como públicos en el modelo
    (organismo, fechas, resumen y certificado si corresponde); nunca se
    exponen observaciones internas ni datos de evaluadores.
    """
    carrera = get_object_or_404(CarreraAcreditada.objects.prefetch_related("imagenes"), slug=slug, publicado=True)
    return render(
        request,
        "acreditacion/detalle.html",
        {"carrera": carrera, "imagenes": carrera.imagenes.all()},
    )
