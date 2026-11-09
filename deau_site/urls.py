from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView

from .sitemaps import sitemaps

# Las direcciones públicas son las mismas de siempre; cada dominio aporta sus propias rutas.
urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots_txt",
    ),
    path("deau/", include("apps.institucional.urls")),
    path("procesos/", include("apps.procesos.urls")),
    path("carreras-acreditadas/", include("apps.acreditacion.urls")),
    path("documentos/", include("apps.documentos.urls")),
    path("convocatorias/", include("apps.convocatorias.urls")),
    path("noticias/", include("apps.noticias.urls")),
    path("contacto/", include("apps.contacto.urls")),
    path("panel/", include("apps.panel.urls")),
    path("editor/", include("apps.editor.urls")),
    path("", include("apps.accounts.urls")),     # login/, logout/, sesion/ping/
    path("", include("apps.inicio.urls")),       # página de inicio
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
