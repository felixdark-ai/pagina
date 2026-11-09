from .models import InformacionContacto


def contacto_global(request):
    """Información de contacto institucional, disponible en todas las plantillas (pie de página)."""
    return {"contacto_global": InformacionContacto.cargar()}
