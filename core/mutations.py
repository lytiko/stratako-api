import json
import graphene
import requests
from graphql import GraphQLError
from django.utils import timezone
from .forms import *

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



class UpdateEmailMutation(graphene.Mutation):
    """Updates the email of a user, and returns that new email."""

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
    
    email = graphene.String()

    def mutate(self, info, **kwargs):
        form = UpdateEmailForm(kwargs, instance=info.context.user)
        if form.is_valid():
            form.save()
            return UpdateEmailMutation(email=form.instance.email)
        raise GraphQLError(json.dumps(form.errors))



class UpdatePasswordMutation(graphene.Mutation):
    """Updates the password of a user, and returns a success indicator."""

    class Arguments:
        current = graphene.String(required=True)
        new = graphene.String(required=True)
    
    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        form = UpdatePasswordForm(kwargs, instance=info.context.user)
        if form.is_valid():
            form.save()
            return UpdatePasswordMutation(success=True)
        raise GraphQLError(json.dumps(form.errors))



class UpdateBasicSettingsMutation(graphene.Mutation):
    """Updates app-wide settings."""

    class Arguments:
        day_ends = graphene.Int(required=True)
        timezone = graphene.String(required=False)
    
    user = graphene.Field("core.queries.UserType")

    def mutate(self, info, **kwargs):
        user = info.context.user
        form = UpdateBasicSettingsForm(kwargs, instance=user)
        if form.is_valid():
            form.save()
            return UpdateBasicSettingsMutation(user=user)
        raise GraphQLError(json.dumps(form.errors))



class DeleteUserMutation(graphene.Mutation):
    """Deletes a user account and all its objects, if a password is correct."""

    class Arguments:
        password = graphene.String(required=True)
    
    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        if info.context.user.check_password(kwargs["password"]):
            info.context.user.delete()
            return DeleteUserMutation(success=True)
        raise GraphQLError(json.dumps({"password": ["Password not correct"]}))
        

