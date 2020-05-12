import os
from .secrets import SECRET_KEY, BASE_DIR, DATABASES

ALLOWED_HOSTS = []

DEBUG = True

ROOT_URLCONF = "core.urls"

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "django.contrib.auth",
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
    "core.middleware.AuthenticationMiddleware",
]

AUTH_USER_MODEL = "core.User"
AUTH_PASSWORD_VALIDATORS = [{
    "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    "OPTIONS": {"min_length": 9}
},{
    "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
}, {
    "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
}]

STATIC_URL = "/static/"

CORS_ORIGIN_ALLOW_ALL = True

TOKEN_TIMEOUT = 15

GRAPHENE = {
    "SCHEMA": "core.schema.schema"
}
