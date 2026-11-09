from django.conf import settings


def sesion(request):
    """Cada cuántos segundos la página abierta avisa que hay actividad (mantiene viva la sesión)."""
    return {
        "SESION_PING_SEGUNDOS": max(15, min(settings.SESION_PING_SEGUNDOS, settings.SESSION_COOKIE_AGE // 3)),
    }
