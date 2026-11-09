from django import template
from django.utils.safestring import mark_safe

from apps.core.sanitizar import limpiar_html

register = template.Library()


@register.filter(is_safe=True)
def html_seguro(valor):
    """Muestra HTML del editor tras limpiarlo (sustituye al peligroso ``|safe``)."""
    return mark_safe(limpiar_html(valor))
