from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.views.decorators.http import require_GET


class LoginInstitucional(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


@require_GET
def sesion_ping(request):
    """
    La página abierta avisa aquí, de forma silenciosa, mientras la persona está trabajando
    (escribiendo, moviendo el mouse…) para que la sesión no caduque por inactividad.
    Si la sesión ya caducó responde 401.
    """
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    respuesta = HttpResponse(status=204)
    respuesta["Cache-Control"] = "no-store"
    return respuesta
