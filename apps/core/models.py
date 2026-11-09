from django.db import models


class SingletonModel(models.Model):
    """
    Modelo base para contenidos de los que solo debe existir una fila editable
    (ej. Hero de inicio, datos de la DEAU, datos de contacto).
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # No se permite borrar contenido singleton, solo editarlo.

    @classmethod
    def cargar(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
