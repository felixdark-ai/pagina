from datetime import date

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.core.testing import BaseTest, imagen

from .models import CarreraAcreditada, CarreraImagen


class CarrerasTests(BaseTest):
    def _carrera(self, nombre, ambito, **extra):
        return CarreraAcreditada.objects.create(
            nombre=nombre,
            ambito=ambito,
            escudo=imagen(f"{nombre}.png"),
            fecha_acreditacion=date(2024, 5, 1),
            resumen_publico="Resumen público.",
            **extra,
        )

    def test_se_separan_nacionales_e_internacionales(self):
        self._carrera("Civil", "nacional")
        self._carrera("Derecho", "nacional")
        self._carrera("Sistemas", "internacional")
        r = self.client.get(reverse("inicio:inicio"))
        self.assertEqual([c.nombre for c in r.context["carreras_nacionales"]], ["Civil", "Derecho"])
        self.assertEqual([c.nombre for c in r.context["carreras_internacionales"]], ["Sistemas"])
        self.assertContains(r, "Acreditadas nacionalmente")
        self.assertContains(r, "Acreditadas internacionalmente")

    def test_si_no_hay_internacionales_no_se_muestra_ese_bloque(self):
        self._carrera("Civil", "nacional")
        r = self.client.get(reverse("inicio:inicio"))
        self.assertContains(r, "Acreditadas nacionalmente")
        self.assertNotContains(r, "Acreditadas internacionalmente")

    def test_detalle_muestra_sello_certificado_y_galeria(self):
        c = self._carrera(
            "Civil",
            "internacional",
            certificado_publico=SimpleUploadedFile("cert.pdf", b"%PDF-1.4 test", content_type="application/pdf"),
        )
        CarreraImagen.objects.create(carrera=c, imagen=imagen("p1.png"), descripcion="Visita de pares")
        CarreraImagen.objects.create(carrera=c, imagen=imagen("p2.png"))
        r = self.client.get(c.get_absolute_url())
        self.assertContains(r, "Carrera acreditada")
        self.assertContains(r, 'class="sello"')
        self.assertContains(r, "Certificado de acreditación")
        # Visor propio con PDF.js (no depende del visor nativo del navegador)
        self.assertContains(r, "data-visor-pdf")
        self.assertContains(r, 'data-src="/media/carreras/certificados/')
        self.assertContains(r, "pdf.worker.min.js")
        self.assertContains(r, "pdf.min.js")
        self.assertContains(r, "acreditacion/js/visor_pdf.js")      # el código del visor vive en esta app
        self.assertNotContains(r, 'type="application/pdf"')
        self.assertContains(r, "Fotos del proceso de acreditación")
        self.assertContains(r, "data-lightbox", count=2)
        self.assertContains(r, "Visita de pares")

    def test_detalle_sin_extras_no_muestra_secciones_vacias(self):
        c = self._carrera("Civil", "nacional")
        r = self.client.get(c.get_absolute_url())
        self.assertContains(r, 'class="sello"')
        self.assertNotContains(r, "Certificado de acreditación")
        self.assertNotContains(r, "Fotos del proceso")

    def test_certificado_en_imagen(self):
        c = self._carrera("Civil", "nacional", certificado_publico=imagen("cert.png"))
        self.assertTrue(c.certificado_es_imagen)
        r = self.client.get(c.get_absolute_url())
        self.assertContains(r, "certificado__imagen")

    def test_certificado_rechaza_extensiones_no_permitidas(self):
        c = self._carrera("Civil", "nacional")
        c.certificado_publico = SimpleUploadedFile("x.exe", b"MZ")
        with self.assertRaises(ValidationError):
            c.full_clean()


class VisorPdfTests(BaseTest):
    def test_sitio_no_se_puede_incrustar_en_otros_sitios(self):
        """El visor usa canvas (PDF.js), por lo que no se necesitan marcos: se mantiene DENY."""
        r = self.client.get(reverse("inicio:inicio"))
        self.assertEqual(r.headers.get("X-Frame-Options"), "DENY")

    def test_archivos_de_pdfjs_incluidos(self):
        from pathlib import Path

        base = Path(__file__).parent / "static" / "acreditacion" / "vendor" / "pdfjs"
        for nombre in ("pdf.min.js", "pdf.worker.min.js", "LICENSE"):
            self.assertTrue((base / nombre).exists(), nombre)

    def test_carrera_con_imagen_no_carga_pdfjs(self):
        c = CarreraAcreditada.objects.create(
            nombre="Img", ambito="nacional", escudo=imagen("e.png"), fecha_acreditacion=date(2024, 1, 1),
            resumen_publico="r", certificado_publico=imagen("c.png"),
        )
        r = self.client.get(c.get_absolute_url())
        self.assertNotContains(r, "pdf.min.js")
        self.assertNotContains(r, "visor_pdf.js")
        self.assertNotContains(r, "data-visor-pdf")


class CarreraNoPublicadaTests(BaseTest):
    def test_documento_no_publicado_no_es_accesible(self):
        c = CarreraAcreditada.objects.create(
            nombre="Oculta", ambito="nacional", escudo=imagen("o.png"), fecha_acreditacion=date(2024, 1, 1),
            resumen_publico="r", publicado=False,
        )
        self.assertEqual(self.client.get(c.get_absolute_url()).status_code, 404)
