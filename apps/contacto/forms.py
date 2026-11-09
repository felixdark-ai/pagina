from django import forms

from .models import MensajeContacto


class ContactoForm(forms.ModelForm):
    # Campo trampa anti-spam: las personas no lo ven; los bots suelen rellenarlo.
    sitio_web = forms.CharField(required=False, widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}))

    class Meta:
        model = MensajeContacto
        fields = ["nombre", "correo", "asunto", "mensaje"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Tu nombre completo", "maxlength": 150, "autocomplete": "name"}),
            "correo": forms.EmailInput(attrs={"class": "form-control", "placeholder": "tu.correo@ejemplo.com", "autocomplete": "email"}),
            "asunto": forms.TextInput(attrs={"class": "form-control", "placeholder": "Asunto del mensaje", "maxlength": 200}),
            "mensaje": forms.Textarea(attrs={"class": "form-control", "placeholder": "Escribe tu mensaje...", "rows": 6}),
        }

    def full_clean(self):
        """Tras validar, enlaza cada error con su campo para lectores de pantalla (WCAG 3.3.1)."""
        super().full_clean()
        for nombre, campo in self.fields.items():
            if nombre in self.errors:
                campo.widget.attrs["aria-invalid"] = "true"
                campo.widget.attrs["aria-describedby"] = f"error-{nombre}"

    def es_spam(self):
        return bool(self.cleaned_data.get("sitio_web"))

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if len(nombre) < 3:
            raise forms.ValidationError("Por favor ingresa tu nombre completo.")
        return nombre

    def clean_mensaje(self):
        mensaje = self.cleaned_data["mensaje"].strip()
        if len(mensaje) < 10:
            raise forms.ValidationError("El mensaje es demasiado corto. Por favor, cuéntanos más detalles.")
        return mensaje
