"""
Configuración de Django para el sitio institucional de la
Dirección de Evaluación y Acreditación Universitaria (DEAU).

Todas las variables sensibles se leen desde un archivo .env
(ver .env.example en la raíz del proyecto) usando python-decouple.
"""

from datetime import timedelta
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Seguridad básica
# ---------------------------------------------------------------------------
SECRET_KEY = config("SECRET_KEY", default="inseguro-clave-de-desarrollo-cambiar-en-produccion")

DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())

# ---------------------------------------------------------------------------
# Aplicaciones instaladas
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    "axes",                # límite de intentos fallidos de inicio de sesión
]

# Aplicaciones propias: una por dominio (carpeta apps/)
INSTALLED_APPS += [
    "apps.core",           # núcleo compartido: plantilla base, estilos, validadores, sanitizador
    "apps.accounts",       # inicio de sesión, cierre automático y control de sesiones
    "apps.panel",          # panel de control del personal
    "apps.editor",         # editor de texto (Jodit) y subida de imágenes
    "apps.inicio",         # página de inicio: hero, sellos, indicadores, testimonios
    "apps.institucional",  # la DEAU: misión, visión, equipo, valores
    "apps.procesos",       # procesos y acceso a sistemas externos
    "apps.acreditacion",   # carreras acreditadas
    "apps.documentos",     # repositorio documental
    "apps.convocatorias",  # convocatorias
    "apps.noticias",       # noticias y eventos
    "apps.contacto",       # datos de contacto y formulario
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "apps.accounts.middleware.ControlDeSesion",   # cierre de sesión por reinicio / duración máxima
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",   # siempre al final
]

ROOT_URLCONF = "deau_site.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.sitio_config",
                "apps.contacto.context_processors.contacto_global",
                "apps.accounts.context_processors.sesion",
            ],
        },
    },
]

WSGI_APPLICATION = "deau_site.wsgi.application"

# ---------------------------------------------------------------------------
# Base de datos: PostgreSQL exclusivamente, configurada vía variables de entorno.
# El driver es psycopg (versión 3): Django detecta automáticamente el paquete
# "psycopg" instalado y lo usa con el mismo ENGINE "postgresql" de siempre.
# ---------------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="deau_db"),
        "USER": config("DB_USER", default="deau_user"),
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        "CONN_MAX_AGE": 60,
    }
}

# ---------------------------------------------------------------------------
# Validación de contraseñas
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internacionalización
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "es"
TIME_ZONE = config("TIME_ZONE", default="America/La_Paz")
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Archivos estáticos y media
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
# Los estáticos viven dentro de cada app (apps/<app>/static/<app>/) y se encuentran solos.
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# WhiteNoise sirve los estáticos ya comprimidos/versionados directamente
# desde Django/Gunicorn, sin necesidad de configurar Nginx para ese fin.
# El backend con manifiesto (hashes en el nombre de archivo) solo se activa
# en producción, ya que requiere haber ejecutado "collectstatic" antes.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": (
            "apps.core.storage.EstaticosTolerantes"
            if not DEBUG
            else "django.contrib.staticfiles.storage.StaticFilesStorage"
        ),
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Editor de texto de las noticias (Jodit, licencia MIT)
# El contenido se limpia en el servidor (apps/core/sanitizar.py) al guardar y al mostrar.
# Las imágenes se suben desde el propio editor y se guardan en media/editor/AAAA/MM/
# ---------------------------------------------------------------------------
EDITOR_CARPETA_IMAGENES = "editor"
EDITOR_EXTENSIONES_IMAGEN = ["jpg", "jpeg", "png", "gif", "webp"]
EDITOR_MAX_IMAGEN_MB = 10

# ---------------------------------------------------------------------------
# Sesiones
#  - Se cierran tras N minutos SIN actividad (la caducidad se renueva con cada petición;
#    mientras la persona trabaja en una página, un aviso silencioso mantiene viva la sesión).
#  - Se cierran al cerrar el navegador.
#  - Tienen una duración máxima aunque haya actividad continua.
#  - Se cierran al reiniciar el servidor (ver apps/accounts/middleware.py).
# ---------------------------------------------------------------------------
SESSION_COOKIE_AGE = config("SESION_INACTIVIDAD_MINUTOS", default=30, cast=int) * 60
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESION_DURACION_MAXIMA = config("SESION_DURACION_MAXIMA_HORAS", default=8, cast=int) * 3600
SESION_PING_SEGUNDOS = 300
CERRAR_SESIONES_AL_REINICIAR = config("CERRAR_SESIONES_AL_REINICIAR", default=True, cast=bool)
# Si el sitio se ejecuta con VARIOS procesos (p. ej. varios workers de gunicorn), todos deben
# compartir el mismo valor, que cambie en cada reinicio del servicio. Vacío = uno por proceso.
INSTANCIA_SERVIDOR = config("INSTANCIA_SERVIDOR", default="")

# ---------------------------------------------------------------------------
# Límite de intentos fallidos de inicio de sesión (django-axes)
# Aplica a /login/ y a /admin/login/. Se bloquea por NOMBRE DE USUARIO (y no por IP) para
# que funcione igual detrás de un proxy, donde todas las IP parecen la misma. Para desbloquear: python manage.py axes_reset_username USUARIO
# ---------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]
AXES_FAILURE_LIMIT = 5                       # intentos fallidos permitidos
AXES_COOLOFF_TIME = timedelta(minutes=15)    # tiempo de bloqueo
AXES_LOCKOUT_PARAMETERS = ["username"]
AXES_RESET_ON_SUCCESS = True                 # un ingreso correcto reinicia el contador
AXES_LOCKOUT_TEMPLATE = "accounts/bloqueado.html"
AXES_HTTP_RESPONSE_CODE = 429

# axes.W006 recomienda incluir "ip_address". Aquí NO se hace a propósito: detrás de un proxy
# todas las visitas pueden llegar con la misma IP, y bloquear por IP dejaría
# sin acceso a TODO el personal tras 5 errores de cualquier persona. El aviso trata de
# evadir el bloqueo cambiando User-Agent o cookies, lo que no afecta a un bloqueo por usuario.
SILENCED_SYSTEM_CHECKS = ["axes.W006"]

# ---------------------------------------------------------------------------
# Autenticación / login institucional
# ---------------------------------------------------------------------------
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "panel:inicio"
LOGOUT_REDIRECT_URL = "inicio:inicio"

# ---------------------------------------------------------------------------
# Enlaces a los sistemas externos (POA y Desempeño Docente)
# Estos sistemas YA EXISTEN y se desarrollan/mantienen aparte.
# El sitio solo enlaza a ellos; nunca implementa su lógica.
# ---------------------------------------------------------------------------
URL_SISTEMA_POA = config("URL_SISTEMA_POA", default="https://intranet.universidad.edu.bo/poa/")
URL_SISTEMA_DESEMPENO_DOCENTE = config(
    "URL_SISTEMA_DESEMPENO_DOCENTE", default="https://intranet.universidad.edu.bo/desempeno-docente/"
)

# ---------------------------------------------------------------------------
# Correo (para el formulario de contacto)
# ---------------------------------------------------------------------------
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
CONTACTO_EMAIL_DESTINO = config("CONTACTO_EMAIL_DESTINO", default="deau@universidad.edu.bo")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="no-responder@universidad.edu.bo")

# ---------------------------------------------------------------------------
# Seguridad reforzada para producción (activar con DEBUG=False)
# ---------------------------------------------------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# El sitio no debe poder mostrarse dentro de marcos de otros sitios (clickjacking).
X_FRAME_OPTIONS = "DENY"

# ---------------------------------------------------------------------------
# Registro de eventos (ISO 27001: trazabilidad). Salida a consola.
# Se registran errores de servidor y eventos de seguridad.
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "{asctime} {levelname} {name}: {message}", "style": "{"}},
    "handlers": {"consola": {"class": "logging.StreamHandler", "formatter": "simple"}},
    "root": {"handlers": ["consola"], "level": "WARNING"},
    "loggers": {
        "django.security": {"handlers": ["consola"], "level": "WARNING", "propagate": False},
        "django.request": {"handlers": ["consola"], "level": "WARNING", "propagate": False},
    },
}

# Paginación por defecto usada en las vistas de listado
PAGINACION_NOTICIAS = 9
PAGINACION_CONVOCATORIAS = 9
PAGINACION_DOCUMENTOS = 12
