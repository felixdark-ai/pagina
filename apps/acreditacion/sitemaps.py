from django.contrib.sitemaps import Sitemap

from .models import CarreraAcreditada


class CarrerasAcreditadasSitemap(Sitemap):
    priority = 0.6
    changefreq = "monthly"

    def items(self):
        return CarreraAcreditada.objects.filter(publicado=True)

    def location(self, obj):
        return obj.get_absolute_url()
