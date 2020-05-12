import json
import graphene
import requests
from graphql import GraphQLError
from django.utils import timezone
from .forms import SignupForm, LoginForm

class SignupMutation(graphene.Mutation):
    """Creates a user object."""

    class Arguments:
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    token = graphene.String()
    user = graphene.Field("core.queries.UserType")

    def mutate(self, info, **kwargs):
        form = SignupForm(kwargs)
        if form.is_valid():
            form.instance.last_login = timezone.now()
            form.save()
            return SignupMutation(
                user=form.instance, token=form.instance.create_jwt()
            )
        raise GraphQLError(json.dumps(form.errors))



class LoginMutation(graphene.Mutation):
    """Authenticates a user and provides an access token, as well as updating
    the last_login field."""

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    token = graphene.String()
    user = graphene.Field("core.queries.UserType")

    def mutate(self, info, **kwargs):
        form = LoginForm(kwargs)
        user = form.validate_credentials()
        if user:
            user.last_login = timezone.now()
            user.save()
            return LoginMutation(user=user, token=user.create_jwt())
        raise GraphQLError(json.dumps(form.errors))
        

