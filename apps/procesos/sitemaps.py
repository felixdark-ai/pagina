from django.contrib.sitemaps import Sitemap

from .models import Proceso


class ProcesosSitemap(Sitemap):
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        return Proceso.objects.filter(publicado=True, tipo=Proceso.TIPO_INTERNO)

    def location(self, obj):
        return obj.get_absolute_url()
