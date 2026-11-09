from django.contrib import admin

from .models import Convocatoria


@admin.register(Convocatoria)
class ConvocatoriaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "fecha_apertura", "fecha_cierre", "estado", "publicado")
    list_filter = ("estado", "publicado")
    list_editable = ("estado", "publicado")
    prepopulated_fields = {"slug": ("titulo",)}
    search_fields = ("titulo", "descripcion")
