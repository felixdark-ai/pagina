from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    verbose_name = "Acceso y sesiones"

    def ready(self):
        # Registra la señal que marca cada sesión con la ejecución del servidor en que se creó.
        # Debe cargarse al arrancar (y no solo al recibir la primera visita), para que cualquier
        # inicio de sesión —incluso hecho fuera de una petición web— quede correctamente marcado.
        from . import middleware  # noqa: F401
