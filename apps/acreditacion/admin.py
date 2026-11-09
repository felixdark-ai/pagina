from django.contrib import admin

from .models import CarreraAcreditada, CarreraImagen


class CarreraImagenInline(admin.TabularInline):
    model = CarreraImagen
    extra = 3
    fields = ("imagen", "descripcion", "orden")
    verbose_name = "imagen del proceso"
    verbose_name_plural = "Imágenes del proceso de acreditación (opcionales)"


@admin.register(CarreraAcreditada)
class CarreraAcreditadaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "facultad", "ambito", "organismo_acreditador", "fecha_acreditacion", "vigencia_hasta", "orden", "publicado")
    list_editable = ("orden", "publicado")
    list_filter = ("ambito", "organismo_acreditador", "publicado")
    inlines = [CarreraImagenInline]
    prepopulated_fields = {"slug": ("nombre",)}
    search_fields = ("nombre", "facultad")
    ordering = ("orden",)
    fieldsets = (
        ("Carrusel (información visible al público)", {
            "fields": ("nombre", "slug", "facultad", "escudo", "ambito", "orden", "publicado"),
        }),
        ("Detalle de acreditación — SOLO información pública", {
            "description": (
                "⚠️ No incluir datos sensibles (observaciones internas, evaluadores, "
                "puntajes detallados u otra información restringida). Todo lo que se "
                "cargue aquí se muestra públicamente en el sitio."
            ),
            "fields": ("organismo_acreditador", "fecha_acreditacion", "vigencia_hasta", "resumen_publico", "certificado_publico"),
        }),
    )
