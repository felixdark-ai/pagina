from django import forms
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.validators import FileExtensionValidator
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST


class FormularioImagenEditor(forms.Form):
    imagen = forms.ImageField(
        validators=[FileExtensionValidator(settings.EDITOR_EXTENSIONES_IMAGEN)],
        error_messages={"invalid_image": "El archivo no es una imagen válida."},
    )


def _error_editor(mensaje, estado):
    return JsonResponse({"success": False, "data": {"messages": [mensaje], "code": estado}}, status=estado)


@require_POST
def subir_imagen(request):
    """Recibe una imagen desde el editor Jodit y devuelve su URL con el formato que Jodit espera."""
    usuario = request.user
    if not (usuario.is_authenticated and usuario.is_active and usuario.is_staff):
        return _error_editor("No tienes permiso para subir imágenes.", 403)

    archivo = next(iter(request.FILES.values()), None)
    if archivo is None:
        return _error_editor("No se recibió ninguna imagen.", 400)
    if archivo.size > settings.EDITOR_MAX_IMAGEN_MB * 1024 * 1024:
        return _error_editor(f"La imagen supera el máximo de {settings.EDITOR_MAX_IMAGEN_MB} MB.", 400)

    formulario = FormularioImagenEditor(files={"imagen": archivo})
    if not formulario.is_valid():
        mensajes = [m for lista in formulario.errors.values() for m in lista]
        return _error_editor(" ".join(mensajes) or "Archivo no permitido.", 400)

    carpeta = f"{settings.EDITOR_CARPETA_IMAGENES}/{timezone.now():%Y/%m}"
    ruta = default_storage.save(f"{carpeta}/{archivo.name}", archivo)
    url = default_storage.url(ruta)
    base, _, nombre = url.rpartition("/")
    return JsonResponse({
        "success": True,
        "time": timezone.now().isoformat(),
        "data": {"baseurl": base + "/", "messages": [], "files": [nombre], "isImages": [True], "code": 220},
    })
