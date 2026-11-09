from django.urls import reverse

from apps.core.testing import BaseTest

from .models import Proceso


class ProcesosTests(BaseTest):
    def _crear(self, n):
        for i in range(n):
            Proceso.objects.create(titulo=f"Proceso {i}", descripcion_corta="x", orden=i)

    def test_acceso_externo_muestra_ingresar_sin_iniciar_sesion(self):
        proceso = Proceso.objects.create(
            titulo="Sistema de prueba",
            descripcion_corta="Acceso al sistema de prueba.",
            tipo=Proceso.TIPO_EXTERNO,
            url_externa="https://sistema.example/login/",
        )

        respuesta = self.client.get(proceso.get_absolute_url())

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, f"Ingresar a {proceso.titulo}")
        self.assertNotContains(respuesta, "Iniciar sesión para continuar")

    def test_acceso_externo_usa_la_direccion_configurada_en_el_proceso(self):
        proceso = Proceso.objects.create(
            titulo="Sistema de prueba",
            descripcion_corta="Acceso al sistema de prueba.",
            tipo=Proceso.TIPO_EXTERNO,
            url_externa="https://sistema.example/login/",
        )

        respuesta = self.client.get(proceso.get_absolute_url())

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'href="https://sistema.example/login/"')

    def test_redireccion_externa_usa_la_direccion_del_proceso_sin_autenticacion(self):
        proceso = Proceso.objects.create(
            titulo="Sistema de prueba",
            descripcion_corta="Acceso al sistema de prueba.",
            tipo=Proceso.TIPO_EXTERNO,
            url_externa="https://sistema.example/login/",
        )

        respuesta = self.client.get(
            reverse("procesos:redirigir", args=[proceso.slug])
        )

        self.assertRedirects(respuesta, proceso.url_externa, fetch_redirect_response=False)

    def test_proceso_externo_sin_direccion_no_usa_url_predeterminada(self):
        proceso = Proceso.objects.create(
            titulo="Sistema de prueba",
            descripcion_corta="Acceso al sistema de prueba.",
            tipo=Proceso.TIPO_EXTERNO,
        )

        respuesta = self.client.get(proceso.get_absolute_url())

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "La dirección de este sistema aún no está configurada")
        self.assertNotContains(respuesta, "Ingresar a Sistema de prueba")

    def test_muestra_todos_los_procesos_con_3(self):
        self._crear(3)
        r = self.client.get(reverse("inicio:inicio"))
        self.assertEqual(len(r.context["procesos"]), 3)

    def test_muestra_todos_los_procesos_con_8(self):
        self._crear(8)
        r = self.client.get(reverse("inicio:inicio"))
        self.assertEqual(len(r.context["procesos"]), 8)

    def test_no_muestra_no_publicados(self):
        self._crear(2)
        Proceso.objects.create(titulo="Oculto", descripcion_corta="x", publicado=False)
        r = self.client.get(reverse("inicio:inicio"))
        self.assertEqual(len(r.context["procesos"]), 2)
