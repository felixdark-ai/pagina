from django.contrib import admin

from .models import MiembroEquipo, SobreDEAU, ValorInstitucional


@admin.register(SobreDEAU)
class SobreDEAUAdmin(admin.ModelAdmin):
    list_display = ("__str__",)

    def has_add_permission(self, request):
        return not SobreDEAU.objects.exists()


@admin.register(MiembroEquipo)
class MiembroEquipoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cargo", "correo", "orden")
    list_editable = ("orden",)
    list_filter = ("cargo",)
    ordering = ("orden",)


@admin.register(ValorInstitucional)
class ValorInstitucionalAdmin(admin.ModelAdmin):
    list_display = ("titulo", "orden")
    list_editable = ("orden",)
    ordering = ("orden",)
