from django.contrib import admin

from .models import InformacionContacto, MensajeContacto


@admin.register(InformacionContacto)
class InformacionContactoAdmin(admin.ModelAdmin):
    list_display = ("correo", "telefono")

    def has_add_permission(self, request):
        return not InformacionContacto.objects.exists()


@admin.register(MensajeContacto)
class MensajeContactoAdmin(admin.ModelAdmin):
    list_display = ("asunto", "nombre", "correo", "fecha_envio", "atendido")
    list_filter = ("atendido",)
    list_editable = ("atendido",)
    readonly_fields = ("nombre", "correo", "asunto", "mensaje", "fecha_envio")
    date_hierarchy = "fecha_envio"

    def has_add_permission(self, request):
        return False
