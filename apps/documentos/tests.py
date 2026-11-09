from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.core.testing import BaseTest


class DocumentosPaginacionTests(BaseTest):
    def test_paginacion_conserva_filtros(self):
        from apps.documentos.models import CategoriaDocumento, Documento

        cat = CategoriaDocumento.objects.create(nombre="Guías")
        for i in range(15):
            Documento.objects.create(
                titulo=f"Guía {i}", categoria=cat, archivo=SimpleUploadedFile(f"d{i}.pdf", b"%PDF")
            )
        r = self.client.get(reverse("documentos:lista"), {"q": "Guía", "categoria": "guias"})
        self.assertContains(r, "q=Gu%C3%ADa")
        self.assertContains(r, "categoria=guias&amp;page=2")


class DocumentosPanelTests(BaseTest):
    def test_el_formulario_del_panel_rechaza_un_ejecutable(self):
        from django.contrib.auth import get_user_model

        from apps.documentos.models import CategoriaDocumento

        self.client.force_login(get_user_model().objects.create_superuser("root", "r@r.com", "x" * 12))
        cat = CategoriaDocumento.objects.create(nombre="Guías")
        r = self.client.post("/admin/documentos/documento/add/", {
            "titulo": "Malo", "categoria": cat.pk, "descripcion": "", "orden": 0, "publicado": "on",
            "archivo": SimpleUploadedFile("malo.exe", b"MZ\x90"),
        })
        self.assertEqual(r.status_code, 200)               # vuelve al formulario con el error
        self.assertContains(r, "Tipo de archivo no permitido")
