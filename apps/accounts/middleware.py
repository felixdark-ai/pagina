"""
Control de sesiones del sitio.

Django, por sí solo, deja la sesión guardada en la base de datos: al detener y volver a
iniciar el servidor, quien ya había iniciado sesión sigue "dentro". Este middleware añade:

1. Cierre de sesión al REINICIAR el servidor: cada sesión se marca con el identificador de la
   ejecución en la que se creó; si el servidor se reinicia, ese identificador cambia y las
   sesiones anteriores se cierran en su siguiente visita.
2. Duración MÁXIMA de la sesión (SESION_DURACION_MAXIMA), aunque haya actividad continua.

El cierre por INACTIVIDAD lo resuelve Django con SESSION_COOKIE_AGE + SESSION_SAVE_EVERY_REQUEST
(ver settings.py): la caducidad se renueva con cada petición.
"""
import time
import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

# Identificador de esta ejecución del servidor (cambia cada vez que el proceso arranca)
_ID_PROCESO = uuid.uuid4().hex

CLAVE_INSTANCIA = "_instancia_servidor"
CLAVE_INICIO = "_inicio_sesion"


def instancia_actual():
    return settings.INSTANCIA_SERVIDOR or _ID_PROCESO


@receiver(user_logged_in)
def marcar_sesion(sender, request, user, **kwargs):
    """Al iniciar sesión se anota en qué ejecución del servidor y cuándo empezó."""
    sesion = getattr(request, "session", None)
    if sesion is not None:
        sesion[CLAVE_INSTANCIA] = instancia_actual()
        sesion[CLAVE_INICIO] = int(time.time())


class ControlDeSesion:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            motivo = self._motivo_de_cierre(request.session)
            if motivo:
                logout(request)  # vacía la sesión y deja al usuario como anónimo
                messages.info(request, motivo)
        return self.get_response(request)

    @staticmethod
    def _motivo_de_cierre(sesion):
        if settings.CERRAR_SESIONES_AL_REINICIAR and sesion.get(CLAVE_INSTANCIA) != instancia_actual():
            return "Tu sesión se cerró porque el servidor se reinició. Inicia sesión nuevamente."
        inicio = sesion.get(CLAVE_INICIO)
        if inicio is None:
            sesion[CLAVE_INICIO] = int(time.time())     # sesión anterior a esta función: empieza a contar ahora
        elif time.time() - inicio > settings.SESION_DURACION_MAXIMA:
            horas = settings.SESION_DURACION_MAXIMA // 3600
            return f"Tu sesión alcanzó la duración máxima de {horas} horas. Inicia sesión nuevamente."
        return None
