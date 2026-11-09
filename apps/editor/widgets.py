from django import forms
from django.urls import reverse


class EditorJodit(forms.Textarea):
    """Editor de texto enriquecido (Jodit, licencia MIT) para campos de texto largo."""

    class Media:
        css = {"all": ["editor/vendor/jodit/jodit.min.css", "editor/css/editor-admin.css"]}
        js = ["editor/vendor/jodit/jodit.min.js", "editor/js/editor.js"]

    def get_context(self, name, value, attrs):
        contexto = super().get_context(name, value, attrs)
        contexto["widget"]["attrs"]["data-editor-jodit"] = "1"
        contexto["widget"]["attrs"]["data-url-subida"] = reverse("editor:subir_imagen")
        return contexto
