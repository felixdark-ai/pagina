from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render

from .forms import ContactoForm


def formulario(request):
    if request.method == "POST":
        form = ContactoForm(request.POST)
        if form.is_valid() and form.es_spam():
            # Un bot rellenó el campo trampa: se responde igual que a una persona, sin guardar ni enviar nada.
            messages.success(request, "Tu mensaje fue enviado correctamente. Te responderemos a la brevedad.")
            return redirect("contacto:formulario")
        if form.is_valid():
            mensaje = form.save()
            try:
                send_mail(
                    subject=f"[Sitio DEAU] {mensaje.asunto}",
                    message=f"De: {mensaje.nombre} <{mensaje.correo}>\n\n{mensaje.mensaje}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACTO_EMAIL_DESTINO],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, "Tu mensaje fue enviado correctamente. Te responderemos a la brevedad.")
            return redirect("contacto:formulario")
    else:
        form = ContactoForm()
    return render(request, "contacto/formulario.html", {"form": form})
