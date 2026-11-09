
from datetime import timedelta
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY", default="inseguro-clave-de-desarrollo-cambiar-en-produccion")

DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    "axes",            
]

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
    "apps.accounts.middleware.ControlDeSesion", 
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
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
                "apps.contacto.context_processors.contacto_global",
                "apps.accounts.context_processors.sesion",
            ],
        },
    },
]

WSGI_APPLICATION = "deau_site.wsgi.application"

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

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es"
TIME_ZONE = config("TIME_ZONE", default="America/La_Paz")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

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

EDITOR_CARPETA_IMAGENES = "editor"
EDITOR_EXTENSIONES_IMAGEN = ["jpg", "jpeg", "png", "gif", "webp"]
EDITOR_MAX_IMAGEN_MB = 10

SESSION_COOKIE_AGE = config("SESION_INACTIVIDAD_MINUTOS", default=30, cast=int) * 60
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESION_DURACION_MAXIMA = config("SESION_DURACION_MAXIMA_HORAS", default=8, cast=int) * 3600
SESION_PING_SEGUNDOS = 300
CERRAR_SESIONES_AL_REINICIAR = config("CERRAR_SESIONES_AL_REINICIAR", default=True, cast=bool)

INSTANCIA_SERVIDOR = config("INSTANCIA_SERVIDOR", default="")


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

SILENCED_SYSTEM_CHECKS = ["axes.W006"]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "panel:inicio"
LOGOUT_REDIRECT_URL = "inicio:inicio"

EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
CONTACTO_EMAIL_DESTINO = config("CONTACTO_EMAIL_DESTINO", default="deau@universidad.edu.bo")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="no-responder@universidad.edu.bo")

if not DEBUG:
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = "DENY"


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

PAGINACION_NOTICIAS = 9
PAGINACION_CONVOCATORIAS = 9
PAGINACION_DOCUMENTOS = 12
