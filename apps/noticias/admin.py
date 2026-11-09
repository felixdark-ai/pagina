from django.contrib import admin

from apps.editor.widgets import EditorJodit

from .models import Noticia, NoticiaImagen


class NoticiaImagenInline(admin.TabularInline):
    model = NoticiaImagen
    extra = 3
    fields = ("imagen", "pie", "orden")
    verbose_name = "imagen"
    verbose_name_plural = "Galería de imágenes (puedes agregar una o varias)"


@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "fecha", "creado", "tiene_video", "publicado")
    list_filter = ("publicado",)
    list_editable = ("publicado",)
    prepopulated_fields = {"slug": ("titulo",)}
    search_fields = ("titulo", "resumen", "contenido")
    date_hierarchy = "fecha"
    readonly_fields = ("creado",)
    inlines = [NoticiaImagenInline]
    fieldsets = (
        ("Datos de la noticia", {"fields": ("titulo", "slug", "resumen", "fecha", "creado", "publicado")}),
        ("Contenido", {"fields": ("contenido",)}),
        (
            "Multimedia",
            {
                "description": "La portada se muestra en las tarjetas. Agrega un video (archivo o enlace de YouTube/Vimeo) "
                "y, más abajo, las imágenes de la galería.",
                "fields": ("imagen", "video_archivo", "video_url"),
            },
        ),
        ("Sitio externo", {"fields": ("enlace_externo",)}),
    )

    @admin.display(boolean=True, description="Video")
    def tiene_video(self, obj):
        return obj.tiene_video

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "contenido":
            kwargs["widget"] = EditorJodit()
        return super().formfield_for_dbfield(db_field, request, **kwargs)
