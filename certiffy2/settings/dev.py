import ast
import os
import logging
from .base import *

logging.basicConfig(level=logging.INFO)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ast.literal_eval(os.getenv("DEBUG", "True"))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-kuv9eqa9)ze68+qw$8ls#c8tmsuq(__lq6vcpd3wlxg95len(^")

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ast.literal_eval(os.getenv("ALLOWED_HOSTS", "['*']"))

CORS_ALLOW_ALL_ORIGINS = True

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")

# Installed apps needed for development environment
INSTALLED_APPS.insert(0, 'whitenoise.runserver_nostatic')
INSTALLED_APPS += [
    'drf_spectacular',
]

if ast.literal_eval(os.getenv("DEV_USE_AUDITLOG", "False")):
    INSTALLED_APPS += ['auditlog']
    MIDDLEWARE += ['auditlog.middleware.AuditlogMiddleware']
    logging.info("Se encontró DEV_USE_AUDITLOG en True en las variables de entorno")

# Default authentication classes for DRF, these are not recommended for production for security concerns
if 'REST_FRAMEWORK' in globals():
    REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] += [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ]
    REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS'] = 'drf_spectacular.openapi.AutoSchema'

SPECTACULAR_SETTINGS = {
    'TITLE': 'Your Project API',
    'DESCRIPTION': 'Your project description',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # OTHER SETTINGS
}

try:
    from .auth import *
except ImportError:
    logging.error("No se encontró el archivo auth en settings")
    raise ImportError("No se encontró el archivo auth en settings")

DJANGO_STORAGE_BACKEND = os.getenv("DJANGO_STORAGE_BACKEND", "local")
if DJANGO_STORAGE_BACKEND == "local":
    pass
else:
    logging.info(f"Using Django Storages backend: {DJANGO_STORAGE_BACKEND}")
    try:
        from .storages import *
        STORAGES['default']['BACKEND'] = STORAGES_DEFAULT_BACKEND
        STORAGES['default']['OPTIONS'] = STORAGES_DEFAULT_OPTIONS
    except ImportError:
        logging.error("No storages settings file found")
        raise ImportError("No storages configuration file found")

DATA_UPLOAD_MAX_NUMBER_FIELDS=int(os.getenv("DATA_UPLOAD_MAX_NUMBER_FIELDS", 10000))

try:
    from .local import *
except ImportError:
    pass
