from django.contrib.sitemaps import Sitemap

from .models import Noticia


class NoticiasSitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"

    def items(self):
        return Noticia.objects.filter(publicado=True)

    def lastmod(self, obj):
        return obj.fecha

    def location(self, obj):
        return obj.get_absolute_url()
