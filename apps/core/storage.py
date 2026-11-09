import logging

from django.core.files.storage import FileSystemStorage
from whitenoise.storage import CompressedManifestStaticFilesStorage

logger = logging.getLogger(__name__)


class EstaticosTolerantes(CompressedManifestStaticFilesStorage):
    """
    Almacenamiento de producción de WhiteNoise (archivos comprimidos y con hash), pero
    tolerante: si una plantilla referencia un archivo estático que no existe (p. ej. un logo
    que aún no se copió), la página sigue cargando —con esa imagen rota— y se deja un aviso
    en el registro, en lugar de responder con un error 500 en TODAS las páginas.
    """

    manifest_strict = False

    def url(self, name, force=False):
        try:
            return super().url(name, force)
        except ValueError:
            logger.warning("Archivo estático no encontrado: %s", name)
            return FileSystemStorage.url(self, name)
