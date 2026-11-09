from django.conf import settings


def sitio_config(request):
    """Expone en todas las plantillas las direcciones genéricas de los sistemas externos."""
    return {
        "URL_SISTEMA_POA": settings.URL_SISTEMA_POA,
        "URL_SISTEMA_DESEMPENO_DOCENTE": settings.URL_SISTEMA_DESEMPENO_DOCENTE,
    }
