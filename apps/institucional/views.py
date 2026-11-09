from django.shortcuts import render

from .models import MiembroEquipo, SobreDEAU, ValorInstitucional


def deau(request):
    contexto = {
        "sobre": SobreDEAU.cargar(),
        "valores": ValorInstitucional.objects.all(),
    }
    return render(request, "institucional/deau.html", contexto)


def equipo(request):
    contexto = {
        "director": MiembroEquipo.objects.filter(cargo="director").first(),
        "tecnicos": MiembroEquipo.objects.filter(cargo="tecnico"),
        "administrativos": MiembroEquipo.objects.filter(cargo="administrativo"),
    }
    return render(request, "institucional/equipo.html", contexto)
