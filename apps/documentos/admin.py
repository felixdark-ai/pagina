from django.contrib import admin

from .models import CategoriaDocumento, Documento


@admin.register(CategoriaDocumento)
class CategoriaDocumentoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "orden")
    list_editable = ("orden",)
    prepopulated_fields = {"slug": ("nombre",)}


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "categoria", "fecha", "destacado", "publicado")
    list_filter = ("categoria", "destacado", "publicado")
    list_editable = ("destacado", "publicado")
    search_fields = ("titulo", "descripcion")
    date_hierarchy = "fecha"
