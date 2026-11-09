from datetime import timedelta

from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from apps.core.testing import BaseTest


class BloqueoPorIntentosTests(BaseTest):
    def setUp(self):
        from django.contrib.auth import get_user_model

        self.usuario = get_user_model().objects.create_user("ana", password="Clave-Correcta-123", is_staff=True)
        self.url = reverse("accounts:login")

    def _fallar(self, veces, usuario="ana", url=None):
        respuestas = []
        for _ in range(veces):
            respuestas.append(self.client.post(url or self.url, {"username": usuario, "password": "incorrecta"}))
        return respuestas

    def test_el_quinto_fallo_bloquea(self):
        respuestas = self._fallar(4)
        self.assertTrue(all(r.status_code == 200 for r in respuestas))      # 4 fallos: aún se puede reintentar
        r = self._fallar(1)[0]                                              # 5.º fallo: se activa el bloqueo
        self.assertEqual(r.status_code, 429)
        self.assertContains(r, "Demasiados intentos fallidos", status_code=429)

    def test_el_quinto_intento_si_es_correcto_entra(self):
        self._fallar(4)
        r = self.client.post(self.url, {"username": "ana", "password": "Clave-Correcta-123"})
        self.assertEqual(r.status_code, 302)

    def test_con_la_cuenta_bloqueada_ni_la_clave_correcta_entra(self):
        self._fallar(6)
        r = self.client.post(self.url, {"username": "ana", "password": "Clave-Correcta-123"})
        self.assertEqual(r.status_code, 429)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_el_bloqueo_afecta_a_ese_usuario_y_no_a_los_demas(self):
        from django.contrib.auth import get_user_model

        get_user_model().objects.create_user("luis", password="Otra-Clave-456")
        self._fallar(6)
        r = self.client.post(self.url, {"username": "luis", "password": "Otra-Clave-456"})
        self.assertEqual(r.status_code, 302)                               # luis entra con normalidad

    def test_tambien_protege_el_login_del_admin(self):
        self._fallar(6, url="/admin/login/")
        r = self.client.post("/admin/login/", {"username": "ana", "password": "Clave-Correcta-123", "next": "/admin/"})
        self.assertEqual(r.status_code, 429)

    def test_el_bloqueo_vale_para_ambos_formularios(self):
        self._fallar(6, url="/admin/login/")
        r = self.client.post(self.url, {"username": "ana", "password": "Clave-Correcta-123"})
        self.assertEqual(r.status_code, 429)

    def test_un_ingreso_correcto_reinicia_el_contador(self):
        self._fallar(4)
        r = self.client.post(self.url, {"username": "ana", "password": "Clave-Correcta-123"})
        self.assertEqual(r.status_code, 302)
        self.client.logout()
        respuestas = self._fallar(4)                                       # vuelve a tener sus 5 intentos
        self.assertTrue(all(x.status_code == 200 for x in respuestas))

    def test_el_bloqueo_termina_pasado_el_tiempo(self):
        from datetime import timedelta

        from axes.models import AccessAttempt

        self._fallar(6)
        AccessAttempt.objects.update(attempt_time=timezone.now() - timedelta(minutes=16))
        r = self.client.post(self.url, {"username": "ana", "password": "Clave-Correcta-123"})
        self.assertEqual(r.status_code, 302)

    def test_usuarios_inexistentes_tambien_se_bloquean_sin_revelar_si_existen(self):
        r_existente = self._fallar(6, usuario="ana")[-1]
        r_inexistente = self._fallar(6, usuario="no_existe")[-1]
        self.assertEqual(r_existente.status_code, r_inexistente.status_code)
        self.assertEqual(r_existente.content.count(b"Demasiados"), r_inexistente.content.count(b"Demasiados"))

    def test_la_configuracion_es_la_esperada(self):
        from django.conf import settings

        self.assertEqual(settings.AXES_FAILURE_LIMIT, 5)
        self.assertEqual(settings.AXES_COOLOFF_TIME, timedelta(minutes=15))
        self.assertEqual(settings.AXES_LOCKOUT_PARAMETERS, ["username"])


class LoginTests(BaseTest):
    def test_login_fallido_anuncia_el_error(self):
        r = self.client.post(reverse("accounts:login"), {"username": "x", "password": "y"})
        self.assertContains(r, 'role="alert"')


class SesionesTests(BaseTest):
    PROTEGIDA = "/panel/"          # exige personal autenticado

    def setUp(self):
        from django.contrib.auth import get_user_model

        self.usuario = get_user_model().objects.create_user("ana", password="Clave-Correcta-123", is_staff=True)

    def _entrar(self):
        r = self.client.post(reverse("accounts:login"), {"username": "ana", "password": "Clave-Correcta-123"})
        self.assertEqual(r.status_code, 302)

    def _esta_dentro(self):
        return self.client.get(self.PROTEGIDA).status_code == 200

    # ---- reinicio del servidor ------------------------------------------------
    def test_un_inicio_de_sesion_hecho_fuera_de_una_peticion_queda_marcado(self):
        """force_login / login() usados antes de la primera visita (scripts, pruebas) no deben quedar sin sello."""
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.session["_instancia_servidor"], __import__("apps.accounts.middleware", fromlist=["x"]).instancia_actual())
        self.assertTrue(self._esta_dentro())

    def test_la_sesion_funciona_mientras_el_servidor_no_se_reinicia(self):
        self._entrar()
        self.assertTrue(self._esta_dentro())
        self.assertTrue(self._esta_dentro())

    def test_al_reiniciar_el_servidor_la_sesion_se_cierra(self):
        self._entrar()
        self.assertTrue(self._esta_dentro())
        with override_settings(INSTANCIA_SERVIDOR="nueva-ejecucion-del-servidor"):   # equivale a detener y volver a iniciar
            r = self.client.get(self.PROTEGIDA, follow=True)
            self.assertFalse(r.context["user"].is_authenticated)
            self.assertContains(r, "se reinició")                                    # mensaje claro para la persona
            self.assertEqual(r.redirect_chain[0][1], 302)
            self.assertNotIn("_auth_user_id", self.client.session)

    def test_tras_el_reinicio_se_puede_volver_a_entrar(self):
        self._entrar()
        with override_settings(INSTANCIA_SERVIDOR="otra-ejecucion"):
            self.assertFalse(self._esta_dentro())
            self._entrar()
            self.assertTrue(self._esta_dentro())

    def test_sesion_creada_antes_de_esta_funcion_tambien_se_cierra(self):
        self._entrar()
        sesion = self.client.session
        del sesion["_instancia_servidor"]
        sesion.save()
        self.assertFalse(self._esta_dentro())

    def test_se_puede_desactivar_el_cierre_por_reinicio(self):
        self._entrar()
        with override_settings(INSTANCIA_SERVIDOR="otra-ejecucion", CERRAR_SESIONES_AL_REINICIAR=False):
            self.assertTrue(self._esta_dentro())

    def test_el_reinicio_tambien_cierra_la_sesion_del_admin(self):
        from django.contrib.auth import get_user_model

        get_user_model().objects.create_superuser("jefe", "j@j.com", "x" * 12)
        self.client.post("/admin/login/", {"username": "jefe", "password": "x" * 12, "next": "/admin/"})
        self.assertEqual(self.client.get("/admin/").status_code, 200)
        with override_settings(INSTANCIA_SERVIDOR="otra"):
            r = self.client.get("/admin/")
            self.assertEqual(r.status_code, 302)
            self.assertIn("/admin/login/", r["Location"])

    # ---- duración máxima --------------------------------------------------------
    def test_la_sesion_caduca_al_superar_la_duracion_maxima(self):
        import time

        self._entrar()
        sesion = self.client.session
        sesion["_inicio_sesion"] = int(time.time()) - 9 * 3600     # empezó hace 9 h; el máximo por defecto es 8 h
        sesion.save()
        r = self.client.get(self.PROTEGIDA, follow=True)
        self.assertFalse(r.context["user"].is_authenticated)
        self.assertContains(r, "duración máxima")

    def test_dentro_de_la_duracion_maxima_no_se_cierra(self):
        import time

        self._entrar()
        sesion = self.client.session
        sesion["_inicio_sesion"] = int(time.time()) - 7 * 3600
        sesion.save()
        self.assertTrue(self._esta_dentro())

    # ---- inactividad ---------------------------------------------------------------
    def test_configuracion_por_defecto(self):
        from django.conf import settings

        self.assertEqual(settings.SESSION_COOKIE_AGE, 30 * 60)           # 30 min sin actividad
        self.assertTrue(settings.SESSION_SAVE_EVERY_REQUEST)             # cada petición renueva la caducidad
        self.assertTrue(settings.SESSION_EXPIRE_AT_BROWSER_CLOSE)        # al cerrar el navegador
        self.assertEqual(settings.SESION_DURACION_MAXIMA, 8 * 3600)

    def test_la_sesion_inactiva_caduca(self):
        from datetime import timedelta

        from django.contrib.sessions.models import Session

        self._entrar()
        self.assertTrue(self._esta_dentro())
        Session.objects.update(expire_date=timezone.now() - timedelta(minutes=1))     # pasaron 30 min sin actividad
        r = self.client.get(self.PROTEGIDA)
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login/", r["Location"])

    def test_cada_peticion_renueva_la_caducidad(self):
        from datetime import timedelta

        from django.contrib.sessions.models import Session

        self._entrar()
        Session.objects.update(expire_date=timezone.now() + timedelta(minutes=2))     # le quedaban 2 min
        self.assertTrue(self._esta_dentro())
        restante = Session.objects.get().expire_date - timezone.now()
        self.assertGreater(restante, timedelta(minutes=29))                          # vuelve a tener ~30 min

    def test_la_cookie_de_sesion_no_sobrevive_al_cierre_del_navegador(self):
        r = self.client.post(reverse("accounts:login"), {"username": "ana", "password": "Clave-Correcta-123"})
        cookie = r.cookies["sessionid"]
        self.assertEqual(cookie["max-age"], "")       # sin Max-Age ni Expires = cookie de sesión del navegador
        self.assertEqual(cookie["expires"], "")
        self.assertTrue(cookie["httponly"])

    # ---- aviso de actividad ------------------------------------------------------------
    def test_el_ping_mantiene_viva_la_sesion(self):
        from datetime import timedelta

        from django.contrib.sessions.models import Session

        self._entrar()
        Session.objects.update(expire_date=timezone.now() + timedelta(minutes=2))
        r = self.client.get("/sesion/ping/")
        self.assertEqual(r.status_code, 204)
        self.assertGreater(Session.objects.get().expire_date - timezone.now(), timedelta(minutes=29))

    def test_el_ping_avisa_si_la_sesion_ya_caduco(self):
        self.assertEqual(self.client.get("/sesion/ping/").status_code, 401)

    def test_el_script_de_sesion_solo_se_carga_con_usuario_autenticado(self):
        self.assertNotContains(self.client.get("/"), "accounts/js/sesion.js")
        self._entrar()
        r = self.client.get("/")
        self.assertContains(r, "accounts/js/sesion.js")
        self.assertContains(r, 'data-ping="/sesion/ping/"')
        self.assertContains(r, 'data-intervalo="300"')

    def test_el_script_de_sesion_tambien_esta_en_el_admin(self):
        from django.contrib.auth import get_user_model

        self.client.force_login(get_user_model().objects.create_superuser("jefe", "j@j.com", "x" * 12))
        r = self.client.get("/admin/")
        self.assertContains(r, "accounts/js/sesion.js")
        self.assertContains(r, "Panel de contenido")      # el admin conserva su título propio

    def test_el_login_explica_por_que_se_pide_iniciar_sesion(self):
        r = self.client.get("/login/?next=/panel/")
        self.assertContains(r, "Inicia sesión para continuar")
        self.assertNotContains(self.client.get("/login/"), "Inicia sesión para continuar")
