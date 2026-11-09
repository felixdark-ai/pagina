from django.db import models
from django.utils.text import slugify

from apps.core.validators import FORMATOS_TEXTO, validar_documento


class Convocatoria(models.Model):
    ESTADO_ABIERTA = "abierta"
    ESTADO_CERRADA = "cerrada"
    ESTADO_PROXIMA = "proxima"
    ESTADOS = [
        (ESTADO_PROXIMA, "Próxima"),
        (ESTADO_ABIERTA, "Abierta"),
        (ESTADO_CERRADA, "Cerrada"),
    ]

    titulo = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    descripcion = models.TextField()
    fecha_apertura = models.DateField()
    fecha_cierre = models.DateField()
    archivo = models.FileField(
        upload_to="convocatorias/",
        blank=True,
        null=True,
        validators=[validar_documento],
        help_text=f"Formatos aceptados: {FORMATOS_TEXTO}.",
    )
    estado = models.CharField(max_length=10, choices=ESTADOS, default=ESTADO_ABIERTA)
    publicado = models.BooleanField(default=True)

    class Meta:
        ordering = ["-fecha_apertura"]

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.titulo)
            slug = base
            i = 1
            while Convocatoria.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)
