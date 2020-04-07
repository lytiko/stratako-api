from graphene_django.views import GraphQLView
from django.urls import path
from .views import signup, login

urlpatterns = [
 path("signup/", signup),
 path("login/", login),
 path("", GraphQLView.as_view(graphiql=True)),
]