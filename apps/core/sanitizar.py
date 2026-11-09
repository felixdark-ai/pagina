"""
Limpieza del HTML escrito en el editor de noticias (Jodit).

Solo se conserva lo que el editor puede producir: párrafos, títulos, listas, enlaces,
imágenes, tablas, citas y formato básico. Se eliminan scripts, iframes, formularios,
manejadores de eventos (onclick, onerror…), enlaces ``javascript:`` y estilos peligrosos.
Se aplica al GUARDAR la noticia y otra vez al MOSTRARLA (defensa en profundidad, y cubre
el contenido antiguo creado con editores anteriores).
"""
import nh3

ETIQUETAS = {
    "p", "br", "hr", "strong", "b", "em", "i", "u", "s", "strike", "sub", "sup", "mark", "code", "pre",
    "blockquote", "h2", "h3", "h4", "h5", "ul", "ol", "li",
    "a", "img", "figure", "figcaption",
    "table", "thead", "tbody", "tfoot", "tr", "th", "td", "colgroup", "col",
}

ATRIBUTOS = {
    "a": {"href", "title", "target"},          # rel lo agrega nh3 (noopener noreferrer)
    "img": {"src", "alt", "title", "width", "height", "srcset", "sizes", "style"},
    "figure": {"style"},
    "p": {"style"},
    "h2": {"style"}, "h3": {"style"}, "h4": {"style"},
    "table": {"style", "border", "cellpadding", "cellspacing"},
    "tr": {"style"},
    "col": {"style", "span"},
    "td": {"colspan", "rowspan", "style"},
    "th": {"colspan", "rowspan", "style", "scope"},
    "ol": {"start", "type"},
}

# Clases de imágenes y tablas conservadas (ver estilos en style.css)
CLASES = {
    "figure": {
        "image", "image_resized", "table",
        "image-style-side", "image-style-align-left", "image-style-align-center", "image-style-align-right",
        "image-style-block-align-left", "image-style-block-align-right",
    },
    "img": {"image_resized"},
}

# Solo propiedades de presentación inofensivas (nunca position, z-index, display, etc.)
PROPIEDADES_CSS = {
    "width", "height", "min-width", "max-width", "aspect-ratio",
    "text-align", "vertical-align", "float",
    "margin", "margin-left", "margin-right", "margin-top", "margin-bottom",
    "padding", "border", "border-collapse",
}

_limpiador = nh3.Cleaner(
    tags=ETIQUETAS,
    attributes=ATRIBUTOS,
    allowed_classes=CLASES,
    filter_style_properties=PROPIEDADES_CSS,
    url_schemes={"http", "https", "mailto", "tel"},
    link_rel="noopener noreferrer",
    strip_comments=True,
)


def limpiar_html(valor):
    """Devuelve el HTML sin elementos ni atributos peligrosos."""
    if not valor:
        return ""
    return _limpiador.clean(valor)
