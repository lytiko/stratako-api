import os
from .secrets import SECRET_KEY, BASE_DIR, DATABASES

ALLOWED_HOSTS = []

DEBUG = True

ROOT_URLCONF = "core.urls"

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "graphene_django",
    "corsheaders",
    "core"
]

DATE_FORMAT = "D j M, Y"
USE_TZ = True
TIME_ZONE = "UTC"

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

STATIC_URL = "/static/"

CORS_ORIGIN_ALLOW_ALL = True

TOKEN_TIMEOUT = 15

GRAPHENE = {
    "SCHEMA": "core.schema.schema"
}
