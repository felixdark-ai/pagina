from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from apps.core.testing import MEDIA_TMP, BaseTest, imagen


class EditorJoditTests(BaseTest):
    URL = "/editor/subir-imagen/"

    def setUp(self):
        from django.contrib.auth import get_user_model

        U = get_user_model()
        self.staff = U.objects.create_user("editor", password="x" * 12, is_staff=True)
        self.admin = U.objects.create_superuser("jefe", "j@j.com", "x" * 12)
        self.visitante = U.objects.create_user("visitante", password="x" * 12)

    def test_formulario_de_noticia_usa_jodit(self):
        self.client.force_login(self.admin)
        r = self.client.get("/admin/noticias/noticia/add/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "editor/vendor/jodit/jodit.min.js")
        self.assertContains(r, "editor/vendor/jodit/jodit.min.css")
        self.assertContains(r, "editor/js/editor.js")
        self.assertContains(r, "data-editor-jodit")
        self.assertContains(r, 'data-url-subida="/editor/subir-imagen/"')
        self.assertNotContains(r, "ckeditor")

    def test_archivos_del_editor_incluidos_con_su_licencia(self):
        from pathlib import Path

        base = Path(__file__).parent / "static" / "editor" / "vendor" / "jodit"
        for nombre in ("jodit.min.js", "jodit.min.css", "LICENSE.txt"):
            self.assertTrue((base / nombre).exists(), nombre)
        self.assertIn("MIT", (base / "LICENSE.txt").read_text(encoding="utf-8"))

    def test_subida_de_imagen_responde_con_el_formato_de_jodit(self):
        self.client.force_login(self.staff)
        r = self.client.post(self.URL, {"files[0]": imagen("foto.png")})
        self.assertEqual(r.status_code, 200)
        datos = r.json()
        self.assertTrue(datos["success"])
        self.assertRegex(datos["data"]["baseurl"], r"^/media/editor/\d{4}/\d{2}/$")
        self.assertRegex(datos["data"]["files"][0], r"^foto.*\.png$")
        self.assertEqual(datos["data"]["isImages"], [True])
        from pathlib import Path

        guardado = Path(MEDIA_TMP) / datos["data"]["baseurl"].replace("/media/", "", 1) / datos["data"]["files"][0]
        self.assertTrue(guardado.exists())

    def test_solo_el_personal_puede_subir(self):
        for usuario in (None, self.visitante):
            self.client.logout()
            if usuario:
                self.client.force_login(usuario)
            r = self.client.post(self.URL, {"files[0]": imagen("foto.png")})
            self.assertEqual(r.status_code, 403)
            self.assertFalse(r.json()["success"])

    def test_solo_acepta_post(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(self.URL).status_code, 405)

    def test_rechaza_archivos_que_no_son_imagenes(self):
        self.client.force_login(self.staff)
        casos = [
            SimpleUploadedFile("falsa.png", b"<html><script>alert(1)</script></html>", content_type="image/png"),
            SimpleUploadedFile("pagina.html", b"<html></html>", content_type="text/html"),
            SimpleUploadedFile("programa.exe", b"MZ\x90\x00", content_type="application/octet-stream"),
            SimpleUploadedFile("dibujo.svg", b"<svg onload=alert(1)></svg>", content_type="image/svg+xml"),
        ]
        for archivo in casos:
            r = self.client.post(self.URL, {"files[0]": archivo})
            self.assertEqual(r.status_code, 400, archivo.name)
            self.assertFalse(r.json()["success"])

    def test_rechaza_imagenes_demasiado_grandes(self):
        self.client.force_login(self.staff)
        with override_settings(EDITOR_MAX_IMAGEN_MB=0):
            r = self.client.post(self.URL, {"files[0]": imagen("foto.png")})
        self.assertEqual(r.status_code, 400)
        self.assertIn("máximo", r.json()["data"]["messages"][0])

    def test_sin_archivo_responde_error(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.post(self.URL, {}).status_code, 400)
