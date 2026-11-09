import re

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from apps.core.sanitizar import limpiar_html


_RE_YOUTUBE = re.compile(
    r"(?:youtube\.com/(?:watch\?(?:[^#\s]*&)?v=|embed/|shorts/|live/)|youtu\.be/)([A-Za-z0-9_-]{11})"
)
_RE_VIMEO = re.compile(r"vimeo\.com/(?:video/)?(\d+)")


def video_desde_url(url):
    """
    Reconoce enlaces de YouTube o Vimeo y devuelve un diccionario con la URL
    de inserción (``embed``) y, si existe, una miniatura (``miniatura``).
    Devuelve ``None`` si el enlace no es de un proveedor soportado.
    """
    if not url:
        return None
    m = _RE_YOUTUBE.search(url)
    if m:
        vid = m.group(1)
        return {
            "proveedor": "youtube",
            "embed": f"https://www.youtube-nocookie.com/embed/{vid}",
            "miniatura": f"https://img.youtube.com/vi/{vid}/hqdefault.jpg",
        }
    m = _RE_VIMEO.search(url)
    if m:
        return {
            "proveedor": "vimeo",
            "embed": f"https://player.vimeo.com/video/{m.group(1)}",
            "miniatura": "",
        }
    return None


class Noticia(models.Model):
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    resumen = models.CharField(max_length=300)
    contenido = models.TextField(
        "Contenido",
        blank=True,
        help_text="Opcional si la noticia solo dirige a un sitio externo.",
    )
    imagen = models.ImageField(
        "Imagen de portada",
        upload_to="noticias/%Y/%m/",
        blank=True,
        null=True,
        help_text="Se muestra en las tarjetas y al inicio de la noticia.",
    )
    video_archivo = models.FileField(
        "Video (archivo)",
        upload_to="noticias/videos/%Y/%m/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["mp4", "webm", "ogg"])],
        help_text="Archivo MP4, WebM u OGG. Para videos largos es mejor usar un enlace de YouTube o Vimeo.",
    )
    video_url = models.URLField(
        "Video (YouTube o Vimeo)",
        blank=True,
        help_text="Pega el enlace del video; se mostrará incrustado en la noticia.",
    )
    fecha = models.DateField(default=timezone.now)
    creado = models.DateTimeField(default=timezone.now, editable=False)
    enlace_externo = models.URLField(
        "Enlace externo (más información)",
        blank=True,
        help_text="Si la noticia corresponde a otro sitio, el botón «Más información» dirigirá allí.",
    )
    publicado = models.BooleanField(default=True)

    class Meta:
        # Las más recientes primero: por fecha de la noticia y, a igual fecha,
        # por el momento en que se creó.
        ordering = ["-fecha", "-creado"]

    def __str__(self):
        return self.titulo

    def clean(self):
        super().clean()
        if self.video_url and not video_desde_url(self.video_url):
            raise ValidationError(
                {"video_url": "Usa un enlace de YouTube o Vimeo. Para otros sitios, usa «Enlace externo»."}
            )

    def save(self, *args, **kwargs):
        self.contenido = limpiar_html(self.contenido)
        if not self.slug:
            base = slugify(self.titulo)
            slug = base
            i = 1
            while Noticia.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("noticias:detalle", args=[self.slug])

    # --- Multimedia -------------------------------------------------------
    @property
    def video_embed(self):
        return video_desde_url(self.video_url)

    @property
    def tiene_video(self):
        return bool(self.video_archivo or self.video_embed)

    @property
    def portada_url(self):
        """Imagen para tarjetas: portada, primera foto de la galería o miniatura del video."""
        if self.imagen:
            return self.imagen.url
        primera = next(iter(self.imagenes.all()), None)
        if primera:
            return primera.imagen.url
        embed = self.video_embed
        if embed and embed["miniatura"]:
            return embed["miniatura"]
        return ""

    @property
    def total_imagenes(self):
        return len(self.imagenes.all()) + (1 if self.imagen else 0)


class NoticiaImagen(models.Model):
    """Imágenes adicionales de una noticia (galería)."""

    noticia = models.ForeignKey(Noticia, related_name="imagenes", on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to="noticias/galeria/%Y/%m/")
    pie = models.CharField("Descripción", max_length=200, blank=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden", "id"]
        verbose_name = "Imagen de la noticia"
        verbose_name_plural = "Galería de imágenes"

    def __str__(self):
        return self.pie or f"Imagen {self.orden or self.pk}"
