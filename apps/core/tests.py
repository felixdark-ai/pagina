import tempfile

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from .testing import BaseTest


class EstaticosTolerantesTests(TestCase):
    def test_archivo_estatico_inexistente_no_provoca_error(self):
        from django.test import override_settings

        from apps.core.storage import EstaticosTolerantes

        with tempfile.TemporaryDirectory() as raiz, override_settings(STATIC_ROOT=raiz, STATIC_URL="/static/"):
            almacen = EstaticosTolerantes()
            with self.assertLogs("apps.core.storage", level="WARNING"):
                self.assertEqual(almacen.url("core/img/escudo.png"), "/static/core/img/escudo.png")


class LimpiezaHtmlTests(BaseTest):
    ATAQUES = {
        "script": "<p>Hola</p><script>alert(1)</script>",
        "onerror": '<img src="x" onerror="alert(1)">',
        "javascript": '<a href="javascript:alert(1)">clic</a>',
        "iframe": '<iframe src="https://malo.example"></iframe>',
        "svg": "<svg onload=alert(1)></svg>",
        "form": '<form action="https://malo.example"><input name="x"></form>',
        "style": "<style>body{display:none}</style>",
        "estilo-pantalla": '<p style="position:fixed;top:0;left:0;width:100%;height:100%">x</p>',
        "onclick": '<p onclick="alert(1)">x</p>',
    }

    def test_se_eliminan_elementos_peligrosos(self):
        from apps.core.sanitizar import limpiar_html

        for nombre, html in self.ATAQUES.items():
            salida = limpiar_html(html).lower()
            for peligro in ("<script", "onerror", "javascript:", "<iframe", "<svg", "<form", "<style", "position", "onclick", "onload"):
                self.assertNotIn(peligro, salida, f"{nombre}: quedó {peligro}")

    def test_se_conserva_el_contenido_legitimo(self):
        from apps.core.sanitizar import limpiar_html

        html = (
            '<h2>Título</h2><p>Texto con <strong>negrita</strong> y <em>cursiva</em>.</p>'
            '<ul><li>uno</li></ul><blockquote>cita</blockquote>'
            '<figure class="image image_resized" style="width:50%"><img src="/media/ckeditor_uploads/a.png" alt="Foto" width="600" height="400"></figure>'
            '<figure class="table"><table><tbody><tr><td colspan="2">celda</td></tr></tbody></table></figure>'
            '<a href="https://ejemplo.com" target="_blank">sitio</a>'
        )
        salida = limpiar_html(html)
        for esperado in ("<h2>", "<strong>", "<em>", "<li>", "<blockquote>", 'alt="Foto"', 'width:50%', "<table>", 'colspan="2"', 'href="https://ejemplo.com"'):
            self.assertIn(esperado, salida)
        self.assertIn('rel="noopener noreferrer"', salida)   # los enlaces externos no ceden control a la otra página

    def test_clases_ajenas_se_descartan(self):
        from apps.core.sanitizar import limpiar_html

        salida = limpiar_html('<figure class="image volver-arriba"><img src="/a.png"></figure>')
        self.assertIn('class="image"', salida)
        self.assertNotIn("volver-arriba", salida)


class LimpiezaHtmlJoditTests(BaseTest):
    def test_el_html_tipico_de_jodit_se_conserva_tras_la_limpieza(self):
        from apps.core.sanitizar import limpiar_html

        html = (
            '<h2>Título</h2><p style="text-align: center;">Texto <strong>negrita</strong> <u>sub</u> <s>tach</s></p>'
            '<p><img src="/media/editor/2026/10/a.png" alt="Foto" style="width: 600px; height: 400px;" width="600" height="400"></p>'
            '<table style="border-collapse:collapse;width: 100%;" border="1"><tbody><tr><td style="width: 50%;">1</td><td>2</td></tr></tbody></table>'
            '<blockquote>cita</blockquote><hr><ul><li>uno</li></ul>'
            '<p><a href="https://ejemplo.com" target="_blank">enlace</a></p>'
        )
        salida = limpiar_html(html).replace(" ", "")      # el limpiador normaliza los espacios del CSS
        for esperado in ("<h2>", "text-align:center", "<strong>", "<u>", "<s>", "/media/editor/2026/10/a.png", 'alt="Foto"',
                         "width:600px", "<table", 'border="1"', "border-collapse", "<blockquote>", "<hr>", "<li>", 'href="https://ejemplo.com"'):
            self.assertIn(esperado, salida)

    def test_estilos_peligrosos_de_jodit_se_descartan(self):
        from apps.core.sanitizar import limpiar_html

        salida = limpiar_html('<p style="position:fixed;top:0;left:0;z-index:9999;width:100%">x</p><img src="/a.png" style="display:none;width:10px">')
        self.assertNotIn("position", salida)
        self.assertNotIn("z-index", salida)
        self.assertNotIn("display", salida)
        self.assertIn("width", salida)


class DocumentosValidosTests(BaseTest):
    def _validar(self, nombre, contenido):
        from apps.core.validators import validar_documento

        validar_documento(SimpleUploadedFile(nombre, contenido))

    def test_formatos_validos(self):
        casos = {
            "informe.pdf": b"%PDF-1.7\n1 0 obj",
            "INFORME.PDF": b"%PDF-1.4",
            "acta.docx": b"PK\x03\x04\x14\x00",
            "datos.xlsx": b"PK\x03\x04\x14\x00",
            "slides.pptx": b"PK\x03\x04\x14\x00",
            "antiguo.doc": b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1\x00",
            "antiguo.xls": b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1\x00",
            "libre.odt": b"PK\x03\x04\x14\x00",
            "tabla.csv": "nombre;edad\nAna;30\n".encode(),
        }
        for nombre, contenido in casos.items():
            self._validar(nombre, contenido)   # no debe lanzar error

    def test_extensiones_no_permitidas(self):
        for nombre in ("virus.exe", "pagina.html", "script.js", "imagen.svg", "macro.docm", "paquete.zip", "sin_extension", "archivo.php", "doble.pdf.exe"):
            with self.assertRaises(ValidationError, msg=nombre):
                self._validar(nombre, b"%PDF-1.4 contenido")

    def test_contenido_que_no_corresponde_a_la_extension(self):
        casos = {
            "falso.pdf": b"<html><script>alert(1)</script></html>",   # página web renombrada a .pdf
            "falso.docx": b"MZ\x90\x00 ejecutable",                   # ejecutable renombrado a .docx
            "falso.doc": b"PK\x03\x04",                               # zip con extensión de Word antiguo
            "binario.csv": b"a;b\x00\x01\x02",
        }
        for nombre, contenido in casos.items():
            with self.assertRaises(ValidationError, msg=nombre):
                self._validar(nombre, contenido)

    def test_el_mensaje_de_error_indica_los_formatos_aceptados(self):
        with self.assertRaises(ValidationError) as ctx:
            self._validar("virus.exe", b"MZ")
        texto = " ".join(ctx.exception.messages)
        self.assertIn(".exe", texto)
        self.assertIn("PDF", texto)

    def test_se_aplica_a_todos_los_campos_de_documentos(self):
        from apps.convocatorias.models import Convocatoria
        from apps.documentos.models import Documento
        from apps.procesos.models import DocumentoProceso
        from apps.core.validators import validar_documento

        for modelo in (Documento, DocumentoProceso, Convocatoria):
            self.assertIn(validar_documento, modelo._meta.get_field("archivo").validators, modelo.__name__)


class MigrarDesdeCoreTests(BaseTest):
    """El comando que traslada los datos de las tablas antiguas core_* a las tablas por dominio."""

    def _ejecutar(self):
        from io import StringIO

        from django.core.management import call_command

        salida = StringIO()
        call_command("migrar_desde_core", stdout=salida)
        return salida.getvalue()

    def test_sin_tablas_antiguas_no_hace_nada(self):
        self.assertIn("No había nada que copiar", self._ejecutar())

    def test_copia_los_datos_conservando_ids_y_relaciones(self):
        from django.db import connection

        from apps.documentos.models import CategoriaDocumento, Documento
        from apps.noticias.models import Noticia

        cat = CategoriaDocumento.objects.create(nombre="Guías")
        doc = Documento.objects.create(titulo="Guía 1", categoria=cat, archivo=SimpleUploadedFile("g.pdf", b"%PDF-1.4"))
        noticia = Noticia.objects.create(titulo="Noticia vieja", resumen="r", contenido="<p>x</p>")
        ids = (cat.pk, doc.pk, noticia.pk)

        # Simula la base de la versión anterior: tablas core_* con los mismos datos
        with connection.cursor() as c:
            for tabla in ("categoriadocumento", "documento", "noticia"):
                c.execute(f"CREATE TABLE core_{tabla} AS SELECT * FROM " + {
                    "categoriadocumento": "documentos_categoriadocumento",
                    "documento": "documentos_documento",
                    "noticia": "noticias_noticia"}[tabla])
        Documento.objects.all().delete()
        CategoriaDocumento.objects.all().delete()
        Noticia.objects.all().delete()

        self._ejecutar()

        self.assertEqual(CategoriaDocumento.objects.get().pk, ids[0])
        self.assertEqual(Documento.objects.get().pk, ids[1])
        self.assertEqual(Documento.objects.get().categoria_id, ids[0])
        self.assertEqual(Noticia.objects.get().titulo, "Noticia vieja")

        # Una segunda ejecución no duplica nada (las tablas nuevas ya tienen datos)
        self._ejecutar()
        self.assertEqual(Noticia.objects.count(), 1)
