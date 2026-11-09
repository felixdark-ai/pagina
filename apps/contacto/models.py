from django.db import models

from apps.core.models import SingletonModel


class InformacionContacto(SingletonModel):
    correo = models.EmailField(default="deau@universidad.edu.bo")
    telefono = models.CharField(max_length=50, default="(00) 000-0000")
    direccion = models.CharField(max_length=250, default="Ciudad Universitaria, Edificio de Rectorado")
    horario = models.CharField(max_length=150, default="Lunes a viernes, 08:30 - 16:30")
    facebook = models.URLField(blank=True)
    twitter_x = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    mapa_embed_url = models.URLField(
        blank=True, help_text="URL de inserción (embed) de Google Maps."
    )

    def __str__(self):
        return "Información de contacto"

    class Meta:
        verbose_name = "Información de contacto"
        verbose_name_plural = "Información de contacto"


class MensajeContacto(models.Model):
    nombre = models.CharField(max_length=150)
    correo = models.EmailField()
    asunto = models.CharField(max_length=200)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    atendido = models.BooleanField(default=False)

    class Meta:
        ordering = ["-fecha_envio"]
        verbose_name = "Mensaje de contacto"
        verbose_name_plural = "Mensajes de contacto"

    def __str__(self):
        return f"{self.asunto} — {self.nombre}"
