"""Mapa del sitio: reúne las páginas fijas y los mapas de cada dominio."""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.acreditacion.sitemaps import CarrerasAcreditadasSitemap
from apps.noticias.sitemaps import NoticiasSitemap
from apps.procesos.sitemaps import ProcesosSitemap


class PaginasEstaticasSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "inicio:inicio",
            "institucional:deau",
            "institucional:equipo",
            "procesos:lista",
            "documentos:lista",
            "convocatorias:lista",
            "noticias:lista",
            "contacto:formulario",
        ]

    def location(self, item):
        return reverse(item)


sitemaps = {
    "estaticas": PaginasEstaticasSitemap,
    "procesos": ProcesosSitemap,
    "noticias": NoticiasSitemap,
    "carreras_acreditadas": CarrerasAcreditadasSitemap,
}
