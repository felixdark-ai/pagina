from django.urls import reverse

from apps.core.testing import BaseTest
from apps.noticias.models import Noticia
from apps.procesos.models import Proceso


class PaginasBasicasTests(BaseTest):
    def test_paginas_publicas_responden(self):
        for nombre in (
            "inicio:inicio", "institucional:deau", "institucional:equipo", "procesos:lista", "documentos:lista",
            "convocatorias:lista", "noticias:lista", "contacto:formulario", "accounts:login",
        ):
            r = self.client.get(reverse(nombre))
            self.assertEqual(r.status_code, 200, nombre)

    def test_favicon_usa_una_ruta_absoluta_en_paginas_anidadas(self):
        noticia = Noticia.objects.create(titulo="Noticia de prueba", resumen="Resumen")
        proceso = Proceso.objects.create(titulo="Proceso de prueba", descripcion_corta="Descripción")
        paginas = (
            reverse("contacto:formulario"),
            reverse("noticias:detalle", args=[noticia.slug]),
            reverse("procesos:detalle", args=[proceso.slug]),
            reverse("institucional:deau"),
            reverse("institucional:equipo"),
        )
        etiqueta_favicon = '<link rel="icon" type="image/png" href="/static/core/img/escudo.png">'

        for pagina in paginas:
            with self.subTest(pagina=pagina):
                respuesta = self.client.get(pagina)
                self.assertEqual(respuesta.status_code, 200)
                self.assertContains(respuesta, etiqueta_favicon)

    def test_menu_marca_pagina_actual(self):
        r = self.client.get(reverse("noticias:lista"))
        self.assertContains(r, 'href="/noticias/" aria-current="page"')


class ErroresTests(BaseTest):
    def test_pagina_404_personalizada(self):
        r = self.client.get("/esta-pagina-no-existe/")
        self.assertEqual(r.status_code, 404)
        self.assertContains(r, "No encontramos esa página", status_code=404)

    def test_plantilla_500_es_independiente(self):
        from django.template.loader import render_to_string

        html = render_to_string("500.html")
        self.assertIn("Ocurrió un problema", html)


class RobotsTests(BaseTest):
    def test_robots_incluye_sitemap_con_url_absoluta(self):
        r = self.client.get("/robots.txt", HTTP_HOST="deau.ejemplo.bo")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Sitemap: http://deau.ejemplo.bo/sitemap.xml")
        self.assertContains(r, "Disallow: /admin/")


class RutasPublicasTests(BaseTest):
    """La reorganización por dominios no debe cambiar ninguna dirección pública (enlaces, favoritos, buscadores)."""

    def test_las_direcciones_publicas_son_las_de_siempre(self):
        esperadas = {
            reverse("inicio:inicio"): "/",
            reverse("institucional:deau"): "/deau/",
            reverse("institucional:equipo"): "/deau/equipo/",
            reverse("procesos:lista"): "/procesos/",
            reverse("procesos:detalle", args=["x"]): "/procesos/x/",
            reverse("procesos:acceso", args=["x"]): "/procesos/x/acceso/",
            reverse("procesos:redirigir", args=["x"]): "/procesos/x/ir/",
            reverse("acreditacion:detalle", args=["x"]): "/carreras-acreditadas/x/",
            reverse("documentos:lista"): "/documentos/",
            reverse("convocatorias:lista"): "/convocatorias/",
            reverse("noticias:lista"): "/noticias/",
            reverse("noticias:detalle", args=["x"]): "/noticias/x/",
            reverse("contacto:formulario"): "/contacto/",
            reverse("accounts:login"): "/login/",
            reverse("accounts:logout"): "/logout/",
            reverse("accounts:sesion_ping"): "/sesion/ping/",
            reverse("panel:inicio"): "/panel/",
            reverse("editor:subir_imagen"): "/editor/subir-imagen/",
        }
        for obtenida, esperada in esperadas.items():
            self.assertEqual(obtenida, esperada)


class SitemapTests(BaseTest):
    def test_el_mapa_del_sitio_reune_los_dominios(self):
        from apps.acreditacion.models import CarreraAcreditada
        from apps.core.testing import imagen
        from datetime import date

        Noticia.objects.create(titulo="Noticia del mapa", resumen="r")
        Proceso.objects.create(titulo="Proceso del mapa", descripcion_corta="d")
        CarreraAcreditada.objects.create(
            nombre="Carrera del mapa", escudo=imagen("e.png"), fecha_acreditacion=date(2024, 1, 1), resumen_publico="r"
        )
        r = self.client.get("/sitemap.xml")
        self.assertEqual(r.status_code, 200)
        for ruta in ("/noticias/", "/noticias/noticia-del-mapa/", "/procesos/proceso-del-mapa/",
                     "/carreras-acreditadas/carrera-del-mapa/", "/deau/equipo/", "/contacto/"):
            self.assertContains(r, ruta)


class EstructuraPorDominioTests(BaseTest):
    """Cada app declara su propio espacio de nombres de plantillas y estáticos (apps/<app>/templates/<app>/…)."""

    def test_cada_app_instalada_esta_en_el_paquete_apps(self):
        from django.apps import apps as registro

        propias = [c for c in registro.get_app_configs() if c.name.startswith("apps.")]
        self.assertEqual(
            sorted(c.label for c in propias),
            sorted(["core", "accounts", "panel", "editor", "inicio", "institucional", "procesos",
                    "acreditacion", "documentos", "convocatorias", "noticias", "contacto"]),
        )

    def test_las_plantillas_y_estaticos_de_cada_app_usan_su_propio_nombre(self):
        from pathlib import Path

        from django.apps import apps as registro

        for config in registro.get_app_configs():
            if not config.name.startswith("apps."):
                continue
            raiz = Path(config.path)
            for carpeta in ("templates", "static"):
                if (raiz / carpeta).exists():
                    contenido = [p.name for p in (raiz / carpeta).iterdir()]
                    self.assertEqual(contenido, [config.label], f"{config.label}/{carpeta}")
