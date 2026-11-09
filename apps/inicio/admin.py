from django.contrib import admin

from .models import HeroImagen, HeroInicio, Indicador, SelloConfianza, Testimonio


class HeroImagenInline(admin.TabularInline):
    model = HeroImagen
    extra = 2
    fields = ("imagen", "orden", "activo")
    verbose_name = "imagen del carrusel"
    verbose_name_plural = "Imágenes del carrusel (con 2 o más imágenes el hero rota cada 5 segundos)"


@admin.register(HeroInicio)
class HeroInicioAdmin(admin.ModelAdmin):
    list_display = ("titulo", "subtitulo")
    inlines = [HeroImagenInline]

    def has_add_permission(self, request):
        return not HeroInicio.objects.exists()


@admin.register(SelloConfianza)
class SelloConfianzaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "orden", "url")
    list_editable = ("orden",)
    ordering = ("orden",)


@admin.register(Indicador)
class IndicadorAdmin(admin.ModelAdmin):
    list_display = ("etiqueta", "valor", "orden", "activo")
    list_editable = ("orden", "activo")
    ordering = ("orden",)


@admin.register(Testimonio)
class TestimonioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cargo", "orden", "publicado")
    list_editable = ("orden", "publicado")
    ordering = ("orden",)
