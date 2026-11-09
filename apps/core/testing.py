"""Utilidades compartidas por las pruebas de todas las apps."""
import shutil
import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

MEDIA_TMP = tempfile.mkdtemp(prefix="deau_test_media_")

AJUSTES = dict(
    MEDIA_ROOT=MEDIA_TMP,
    SECURE_SSL_REDIRECT=False,
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    },
)


def imagen(nombre="foto.png", color=(0, 43, 92)):
    buf = BytesIO()
    Image.new("RGB", (40, 30), color).save(buf, "PNG")
    return SimpleUploadedFile(nombre, buf.getvalue(), content_type="image/png")


@override_settings(**AJUSTES)
class BaseTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TMP, ignore_errors=True)
