from django.urls import reverse

from apps.core.testing import BaseTest


class ContactoTests(BaseTest):
    DATOS = {"nombre": "Ana Pérez", "correo": "ana@ejemplo.com", "asunto": "Consulta", "mensaje": "Hola, quisiera más información."}

    def test_contacto_valido_se_guarda(self):
        from apps.contacto.models import MensajeContacto

        r = self.client.post(reverse("contacto:formulario"), self.DATOS)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(MensajeContacto.objects.count(), 1)

    def test_honeypot_descarta_spam_sin_guardar(self):
        from django.core import mail

        from apps.contacto.models import MensajeContacto

        r = self.client.post(reverse("contacto:formulario"), {**self.DATOS, "sitio_web": "http://spam.example"})
        self.assertEqual(r.status_code, 302)  # el bot no nota la diferencia
        self.assertEqual(MensajeContacto.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_errores_de_contacto_estan_asociados_a_su_campo(self):
        r = self.client.post(reverse("contacto:formulario"), {**self.DATOS, "nombre": "A", "mensaje": "corto"})
        self.assertContains(r, 'id="error-nombre"')
        self.assertContains(r, 'role="alert"')
        self.assertContains(r, 'aria-describedby="error-nombre"')
        self.assertContains(r, 'aria-invalid="true"')

    def test_campos_con_autocompletado(self):
        r = self.client.get(reverse("contacto:formulario"))
        self.assertContains(r, 'autocomplete="name"')
        self.assertContains(r, 'autocomplete="email"')
