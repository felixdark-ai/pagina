from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone

from apps.core.testing import BaseTest, imagen

from .models import Noticia, NoticiaImagen, video_desde_url


class NoticiasTests(BaseTest):
    def _noticia(self, titulo, **extra):
        extra.setdefault("contenido", "<p>Cuerpo</p>")
        return Noticia.objects.create(titulo=titulo, resumen="Resumen", **extra)

    def test_orden_mas_recientes_primero(self):
        hoy = timezone.now().date()
        self._noticia("Vieja", fecha=hoy - timedelta(days=10))
        self._noticia("Reciente", fecha=hoy)
        self._noticia("Media", fecha=hoy - timedelta(days=3))
        r = self.client.get(reverse("inicio:inicio"))
        self.assertEqual([n.titulo for n in r.context["noticias"]], ["Reciente", "Media", "Vieja"])

    def test_misma_fecha_gana_la_creada_despues(self):
        hoy = timezone.now().date()
        self._noticia("Primera", fecha=hoy)
        self._noticia("Segunda", fecha=hoy)
        r = self.client.get(reverse("noticias:lista"))
        self.assertEqual([n.titulo for n in r.context["noticias"]], ["Segunda", "Primera"])

    def test_inicio_muestra_solo_las_3_ultimas(self):
        for i in range(5):
            self._noticia(f"N{i}", fecha=date(2026, 1, 1) + timedelta(days=i))
        r = self.client.get(reverse("inicio:inicio"))
        self.assertEqual([n.titulo for n in r.context["noticias"]], ["N4", "N3", "N2"])

    def test_video_youtube_urls(self):
        for url in (
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/watch?feature=share&v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ?t=10",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
        ):
            v = video_desde_url(url)
            self.assertIsNotNone(v, url)
            self.assertEqual(v["embed"], "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ")
            self.assertIn("dQw4w9WgXcQ", v["miniatura"])

    def test_video_vimeo_y_no_soportado(self):
        self.assertEqual(video_desde_url("https://vimeo.com/123456789")["embed"], "https://player.vimeo.com/video/123456789")
        self.assertIsNone(video_desde_url("https://ejemplo.com/video"))
        self.assertIsNone(video_desde_url(""))

    def test_validacion_video_url(self):
        n = Noticia(titulo="T", resumen="R", video_url="https://ejemplo.com/algo")
        with self.assertRaises(ValidationError) as ctx:
            n.full_clean()
        self.assertIn("video_url", ctx.exception.message_dict)

    def test_detalle_con_video_youtube(self):
        n = self._noticia("Con video", video_url="https://youtu.be/dQw4w9WgXcQ")
        r = self.client.get(n.get_absolute_url())
        self.assertContains(r, "youtube-nocookie.com/embed/dQw4w9WgXcQ")
        self.assertContains(r, "<iframe")

    def test_detalle_con_video_archivo(self):
        n = self._noticia(
            "Con archivo", video_archivo=SimpleUploadedFile("v.mp4", b"\x00\x00\x00 ftypmp42", content_type="video/mp4")
        )
        r = self.client.get(n.get_absolute_url())
        self.assertContains(r, "<video controls")

    def test_detalle_con_varias_imagenes(self):
        n = self._noticia("Galeria", imagen=imagen("portada.png"))
        for i in range(3):
            NoticiaImagen.objects.create(noticia=n, imagen=imagen(f"g{i}.png"), pie=f"Foto {i}")
        r = self.client.get(n.get_absolute_url())
        self.assertContains(r, "Galería de imágenes")
        self.assertContains(r, "data-lightbox", count=4)  # portada + 3 de galería
        self.assertEqual(n.total_imagenes, 4)

    def test_enlace_externo_boton_mas_informacion(self):
        n = self._noticia("Externa", contenido="", enlace_externo="https://ejemplo.com/nota")
        r = self.client.get(n.get_absolute_url())
        self.assertContains(r, 'href="https://ejemplo.com/nota"')
        self.assertContains(r, "Más información")
        self.assertContains(r, 'rel="noopener noreferrer"')

    def test_tarjeta_usa_miniatura_de_youtube_si_no_hay_imagen(self):
        n = self._noticia("Solo video", video_url="https://youtu.be/dQw4w9WgXcQ")
        self.assertIn("img.youtube.com/vi/dQw4w9WgXcQ", n.portada_url)
        r = self.client.get(reverse("noticias:lista"))
        self.assertContains(r, "insignia--video")

    def test_tarjeta_usa_primera_foto_de_galeria_si_no_hay_portada(self):
        n = self._noticia("Solo galeria")
        NoticiaImagen.objects.create(noticia=n, imagen=imagen("g.png"))
        self.assertTrue(n.portada_url.endswith(".png"))


class LimpiezaHtmlNoticiasTests(BaseTest):
    def test_noticia_se_guarda_limpia(self):
        n = Noticia.objects.create(titulo="XSS", resumen="r", contenido='<p>ok</p><script>alert(1)</script><img src=x onerror=alert(1)>')
        n.refresh_from_db()
        self.assertEqual(n.contenido.count("<script"), 0)
        self.assertNotIn("onerror", n.contenido)
        self.assertIn("<p>ok</p>", n.contenido)

    def test_detalle_limpia_tambien_contenido_antiguo_ya_guardado(self):
        """Contenido guardado antes de la limpieza (p. ej. con CKEditor 4) tampoco debe ejecutar scripts."""
        n = Noticia.objects.create(titulo="Antigua", resumen="r", contenido="<p>x</p>")
        Noticia.objects.filter(pk=n.pk).update(contenido='<p>texto</p><script>alert(1)</script><a href="javascript:alert(2)">z</a>')
        r = self.client.get(n.get_absolute_url())
        self.assertContains(r, "<p>texto</p>")
        self.assertNotContains(r, "alert(1)")
        self.assertNotContains(r, "javascript:alert")

    def test_la_plantilla_ya_no_usa_safe(self):
        from pathlib import Path

        plantilla = Path(__file__).parent / "templates" / "noticias" / "detalle.html"
        self.assertNotIn("|safe", plantilla.read_text(encoding="utf-8"))
