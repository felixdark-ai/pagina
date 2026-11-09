from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from apps.core.validators import FORMATOS_TEXTO, validar_documento


class Proceso(models.Model):
    TIPO_INTERNO = "interno"
    TIPO_EXTERNO = "externo"
    TIPOS = [
        (TIPO_INTERNO, "Contenido propio del sitio"),
        (TIPO_EXTERNO, "Acceso a sistema externo"),
    ]

    titulo = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    descripcion_corta = models.CharField(max_length=300)
    icono = models.CharField(max_length=50, blank=True, help_text="Nombre de ícono lineal.")
    tipo = models.CharField(max_length=10, choices=TIPOS, default=TIPO_INTERNO)

    # Contenido para procesos internos
    objetivo = models.TextField(blank=True)
    responsables = models.CharField(max_length=250, blank=True)
    etapas = models.TextField(
        blank=True, help_text="Una etapa por línea; se muestran como línea de tiempo."
    )
    preguntas_frecuentes = models.TextField(
        blank=True,
        help_text="Formato: Pregunta::Respuesta, una por línea.",
    )
    contacto_tecnico = models.CharField(max_length=200, blank=True)
    plazo_calendario = models.TextField(blank=True, help_text="Fechas y plazos clave, uno por línea.")

    # Para procesos externos (POA, Desempeño Docente): nombre genérico + URL externa
    url_externa_nombre = models.CharField(
        max_length=100,
        blank=True,
        help_text="Nombre genérico visible del botón, ej. 'Seguimiento al POA'.",
    )
    url_externa = models.URLField(
        blank=True,
        help_text="Dirección completa del sistema externo, incluyendo https://.",
    )

    orden = models.PositiveIntegerField(default=0)
    publicado = models.BooleanField(default=True)

    class Meta:
        ordering = ["orden", "titulo"]

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        if self.tipo == self.TIPO_EXTERNO:
            return reverse("procesos:acceso", args=[self.slug])
        return reverse("procesos:detalle", args=[self.slug])

    def lista_etapas(self):
        return [e.strip() for e in self.etapas.splitlines() if e.strip()]

    def lista_preguntas_frecuentes(self):
        pares = []
        for linea in self.preguntas_frecuentes.splitlines():
            if "::" in linea:
                pregunta, respuesta = linea.split("::", 1)
                pares.append((pregunta.strip(), respuesta.strip()))
        return pares

    def lista_plazos(self):
        return [p.strip() for p in self.plazo_calendario.splitlines() if p.strip()]


class DocumentoProceso(models.Model):
    """Documentos/formatos descargables asociados a un proceso específico."""

    proceso = models.ForeignKey(Proceso, related_name="documentos_asociados", on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    archivo = models.FileField(
        upload_to="procesos/",
        validators=[validar_documento],
        help_text=f"Formatos aceptados: {FORMATOS_TEXTO}.",
    )
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden"]

    def __str__(self):
        return self.titulo
