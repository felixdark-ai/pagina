from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class CarreraAcreditada(models.Model):
    """
    Carreras/programas académicos acreditados que se muestran en un carrusel
    (nombre + escudo). Al hacer clic en el escudo se abre una página de
    detalle con ÚNICAMENTE información pública de la acreditación
    (organismo, fecha, vigencia, resumen y certificado si es público).
    Nunca se almacenan aquí datos sensibles o de uso interno.
    """

    ORGANISMOS = [
        ("ceub", "CEUB"),
        ("arcusur", "ARCU-SUR"),
        ("mercosur", "MERCOSUR"),
        ("otro", "Otro organismo"),
    ]

    AMBITO_NACIONAL = "nacional"
    AMBITO_INTERNACIONAL = "internacional"
    AMBITOS = [
        (AMBITO_NACIONAL, "Acreditada nacionalmente"),
        (AMBITO_INTERNACIONAL, "Acreditada internacionalmente"),
    ]

    nombre = models.CharField(max_length=200, help_text="Nombre de la carrera o programa académico.")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    ambito = models.CharField(
        "Ámbito de la acreditación",
        max_length=15,
        choices=AMBITOS,
        default=AMBITO_NACIONAL,
        help_text="Define en cuál de los dos carruseles del inicio aparece.",
    )
    facultad = models.CharField(max_length=200, blank=True)
    escudo = models.ImageField(
        upload_to="carreras/escudos/",
        help_text="Escudo o logo de la carrera/facultad, mostrado en el carrusel.",
    )
    organismo_acreditador = models.CharField(max_length=20, choices=ORGANISMOS, default="ceub")
    fecha_acreditacion = models.DateField(help_text="Fecha en que se otorgó la acreditación vigente.")
    vigencia_hasta = models.DateField(
        blank=True, null=True, help_text="Fecha hasta la que es vigente la acreditación (dejar en blanco si es indefinida)."
    )
    resumen_publico = models.TextField(
        help_text="Descripción breve y pública del proceso de acreditación de esta carrera. No incluir datos sensibles."
    )
    certificado_publico = models.FileField(
        upload_to="carreras/certificados/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["pdf", "jpg", "jpeg", "png", "webp"])],
        help_text="Certificado o resolución (PDF o imagen), SOLO si es de carácter público.",
    )
    orden = models.PositiveIntegerField(default=0)
    publicado = models.BooleanField(default=True)

    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name = "Carrera acreditada"
        verbose_name_plural = "Carreras acreditadas"

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.nombre)
            slug = base
            i = 1
            while CarreraAcreditada.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("acreditacion:detalle", args=[self.slug])

    @property
    def vigente(self):
        if not self.vigencia_hasta:
            return True
        return self.vigencia_hasta >= timezone.now().date()

    @property
    def certificado_es_pdf(self):
        return bool(self.certificado_publico) and self.certificado_publico.name.lower().endswith(".pdf")

    @property
    def certificado_es_imagen(self):
        return bool(self.certificado_publico) and not self.certificado_es_pdf


class CarreraImagen(models.Model):
    """Fotografías del proceso de acreditación de una carrera (opcionales)."""

    carrera = models.ForeignKey(CarreraAcreditada, related_name="imagenes", on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to="carreras/proceso/")
    descripcion = models.CharField(max_length=200, blank=True, help_text="Breve descripción de la foto.")
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden", "id"]
        verbose_name = "Imagen del proceso"
        verbose_name_plural = "Imágenes del proceso de acreditación"

    def __str__(self):
        return self.descripcion or f"Imagen {self.orden or self.pk}"
