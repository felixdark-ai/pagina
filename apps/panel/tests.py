from django.urls import reverse

from apps.core.testing import BaseTest
from apps.inicio.models import HeroInicio


class PanelTests(BaseTest):
    def test_panel_requiere_staff_y_sus_enlaces_resuelven(self):
        from django.contrib.auth import get_user_model

        self.assertEqual(self.client.get(reverse("panel:inicio")).status_code, 302)
        u = get_user_model().objects.create_user("staff", password="x" * 12, is_staff=True)
        self.client.force_login(u)
        HeroInicio.cargar()
        from apps.contacto.models import InformacionContacto
        from apps.institucional.models import SobreDEAU

        SobreDEAU.cargar()
        InformacionContacto.cargar()
        self.assertEqual(self.client.get(reverse("panel:inicio")).status_code, 200)
