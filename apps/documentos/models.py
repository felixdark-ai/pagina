from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from apps.core.validators import FORMATOS_TEXTO, validar_documento


class CategoriaDocumento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name = "Categoría de documento"
        verbose_name_plural = "Categorías de documentos"

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class Documento(models.Model):
    titulo = models.CharField(max_length=200)
    categoria = models.ForeignKey(CategoriaDocumento, related_name="documentos", on_delete=models.PROTECT)
    archivo = models.FileField(
        upload_to="documentos/%Y/%m/",
        validators=[validar_documento],
        help_text=f"Formatos aceptados: {FORMATOS_TEXTO}.",
    )
    descripcion = models.TextField(blank=True)
    fecha = models.DateField(default=timezone.now)
    destacado = models.BooleanField(default=False)
    publicado = models.BooleanField(default=True)

    class Meta:
        ordering = ["-fecha", "titulo"]

    def __str__(self):
        return self.titulo
