import os
from .secrets import SECRET_KEY, BASE_DIR, DATABASES

ALLOWED_HOSTS = []

DEBUG = True

ROOT_URLCONF = "core.urls"

INSTALLED_APPS = [
 "django.contrib.contenttypes",
 "django.contrib.staticfiles",
 "django.contrib.auth",
 "corsheaders",
 "core",
]

USE_TZ = True
TIME_ZONE = "UTC"

CORS_ORIGIN_ALLOW_ALL = True

TOKEN_TIMEOUT = 15

AUTH_USER_MODEL = "core.User"

MIDDLEWARE = [
 "django.middleware.common.CommonMiddleware",
 "corsheaders.middleware.CorsMiddleware",
 "core.middleware.AuthenticationMiddleware",
]

TEMPLATES = [{
 "BACKEND": "django.template.backends.django.DjangoTemplates",
 "APP_DIRS": True
}]

STATIC_URL = "/static/"
if DEBUG:
    MEDIA_ROOT = os.path.join(BASE_DIR, "uploads")
    STATIC_ROOT = os.path.abspath(f"{BASE_DIR}/static")
else:
     MEDIA_ROOT = os.path.join(BASE_DIR, "..", "uploads")
     STATIC_ROOT = os.path.abspath(f"{BASE_DIR}/../static")
MEDIA_URL = "/uploads/"
SASS_PROCESSOR_ROOT = os.path.abspath(os.path.join(BASE_DIR, "core", "static"))
