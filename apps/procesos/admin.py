from django.contrib import admin

from .models import DocumentoProceso, Proceso


class DocumentoProcesoInline(admin.TabularInline):
    model = DocumentoProceso
    extra = 1


@admin.register(Proceso)
class ProcesoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "tipo", "orden", "publicado")
    list_editable = ("orden", "publicado")
    list_filter = ("tipo", "publicado")
    prepopulated_fields = {"slug": ("titulo",)}
    ordering = ("orden",)
    inlines = [DocumentoProcesoInline]
    fieldsets = (
        ("General", {"fields": ("titulo", "slug", "descripcion_corta", "icono", "tipo", "orden", "publicado")}),
        (
            "Contenido del proceso (solo si es interno)",
            {
                "fields": (
                    "objetivo",
                    "responsables",
                    "etapas",
                    "plazo_calendario",
                    "preguntas_frecuentes",
                    "contacto_tecnico",
                )
            },
        ),
        (
            "Acceso a sistema externo (solo si es externo)",
            {"fields": ("url_externa_nombre", "url_externa")},
        ),
    )
