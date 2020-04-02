from django.urls import path, re_path
from .views import *

urlpatterns = [
 path("signup/", signup),
 path("login/", login),
]