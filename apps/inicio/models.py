from django.db import models

from apps.core.models import SingletonModel


class HeroInicio(SingletonModel):
    titulo = models.CharField(max_length=200, default="Dirección de Evaluación y Acreditación Universitaria")
    subtitulo = models.CharField(
        max_length=300,
        default="Promoviendo la cultura de evaluación y acreditación para la excelencia académica.",
    )
    imagen = models.ImageField(
        "Imagen principal (opcional)",
        upload_to="hero/",
        blank=True,
        null=True,
        help_text="Se muestra primero. Agrega más imágenes abajo para formar un carrusel.",
    )
    boton1_texto = models.CharField(max_length=60, default="Conoce la DEAU")
    boton1_url = models.CharField(max_length=200, default="/deau/")
    boton2_texto = models.CharField(max_length=60, default="Ver procesos")
    boton2_url = models.CharField(max_length=200, default="/procesos/")

    def __str__(self):
        return "Hero de Inicio"

    def slides(self):
        """
        Imágenes que rotan en el hero: la imagen principal (si existe) seguida
        de las imágenes adicionales activas. Con una sola imagen el hero es
        estático; con dos o más se convierte en carrusel.
        """
        urls = []
        if self.imagen:
            urls.append(self.imagen.url)
        for extra in self.imagenes.filter(activo=True):
            urls.append(extra.imagen.url)
        return urls

    class Meta:
        verbose_name = "Hero del inicio"
        verbose_name_plural = "Hero del inicio"


class HeroImagen(models.Model):
    """Imágenes adicionales del hero; con 2 o más se muestra como carrusel."""

    hero = models.ForeignKey(HeroInicio, related_name="imagenes", on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to="hero/")
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["orden", "id"]
        verbose_name = "Imagen del hero"
        verbose_name_plural = "Imágenes del hero (carrusel)"

    def __str__(self):
        return f"Imagen {self.orden or self.pk} del hero"


class SelloConfianza(models.Model):
    """Sellos/textos institucionales de la barra de confianza (CEUB, ARCU-SUR, etc.)."""

    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to="sellos/", blank=True, null=True)
    url = models.URLField(blank=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name = "Sello de confianza"
        verbose_name_plural = "Barra de confianza"

    def __str__(self):
        return self.nombre


class Indicador(models.Model):
    etiqueta = models.CharField(max_length=120, help_text="Ej. 'Unidades académicas acompañadas'")
    valor = models.CharField(max_length=20, help_text="Ej. '12' o '95%'")
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["orden"]
        verbose_name = "Indicador institucional"
        verbose_name_plural = "Indicadores institucionales"

    def __str__(self):
        return f"{self.etiqueta}: {self.valor}"


class Testimonio(models.Model):
    nombre = models.CharField(max_length=150)
    cargo = models.CharField(max_length=150, help_text="Ej. 'Decano, Facultad de...'")
    texto = models.TextField()
    foto = models.ImageField(upload_to="testimonios/", blank=True, null=True)
    orden = models.PositiveIntegerField(default=0)
    publicado = models.BooleanField(default=True)

    class Meta:
        ordering = ["orden"]

    def __str__(self):
        return f"{self.nombre} — {self.cargo}"
