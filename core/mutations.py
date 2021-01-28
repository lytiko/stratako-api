import time
import json
import graphene
from graphql import GraphQLError
from django.contrib.auth.hashers import check_password
from core.models import User, Slot, Project
from core.forms import *
from core.arguments import create_mutation_arguments

class SignupMutation(graphene.Mutation):

    Arguments = create_mutation_arguments(SignupForm)

    access_token = graphene.String()
    user = graphene.Field("core.queries.UserType")

    def mutate(self, info, **kwargs):
        form = SignupForm(kwargs)
        if form.is_valid():
            form.instance.last_login = time.time()
            form.save()
            info.context.refresh_token = form.instance.make_refresh_jwt()
            Slot.objects.create(name="Work", user=form.instance)
            Slot.objects.create(name="Personal", user=form.instance)
            return SignupMutation(
                access_token=form.instance.make_access_jwt(),
                user=form.instance
            )
        raise GraphQLError(json.dumps(form.errors))



class LoginMutation(graphene.Mutation):

    class Arguments:
        email = graphene.String()
        password = graphene.String()
    
    access_token = graphene.String()
    user = graphene.Field("core.queries.UserType")

    def mutate(self, info, **kwargs):
        user = User.objects.filter(email=kwargs["email"]).first()
        if user:
            if check_password(kwargs["password"], user.password):
                info.context.refresh_token = user.make_refresh_jwt()
                user.last_login = time.time()
                user.save()
                return LoginMutation(access_token=user.make_access_jwt(), user=user)
        raise GraphQLError(json.dumps({"email": "Invalid credentials"}))



class LogoutMutation(graphene.Mutation):
    
    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        info.context.refresh_token = False
        return LogoutMutation(success=True)



class UpdateUserMutation(graphene.Mutation):

    Arguments = create_mutation_arguments(UpdateUserForm)
    
    user = graphene.Field("core.queries.UserType")

    def mutate(self, info, **kwargs):
        if not info.context.user:
            raise GraphQLError(json.dumps({"error": "Not authorized"}))
        form = UpdateUserForm(kwargs, instance=info.context.user)
        if form.is_valid():
            form.save()
            return UpdateUserMutation(user=form.instance)
        raise GraphQLError(json.dumps(form.errors))



class UpdatePasswordMutation(graphene.Mutation):

    Arguments = create_mutation_arguments(UpdatePasswordForm)
    
    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        if not info.context.user:
            raise GraphQLError(json.dumps({"error": "Not authorized"}))
        form = UpdatePasswordForm(kwargs, instance=info.context.user)
        if form.is_valid():
            form.save()
            return UpdatePasswordMutation(success=True)
        raise GraphQLError(json.dumps(form.errors))



class UpdateProjectSettingsMutation(graphene.Mutation):

    Arguments = create_mutation_arguments(ProjectSettingsForm)
    
    user = graphene.Field("core.queries.UserType")

    def mutate(self, info, **kwargs):
        if not info.context.user:
            raise GraphQLError(json.dumps({"error": "Not authorized"}))
        form = ProjectSettingsForm(kwargs, instance=info.context.user)
        if form.is_valid():
            form.save()
            return UpdateProjectSettingsMutation(user=form.instance)
        raise GraphQLError(json.dumps(form.errors))



class DeleteUserMutation(graphene.Mutation):

    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        user = info.context.user
        if user:
            user.delete()
            return DeleteUserMutation(success=True)
        raise GraphQLError(json.dumps({"email": ["Invalid or missing token"]}))



class CreateSlotMutation(graphene.Mutation):

    Arguments = create_mutation_arguments(SlotForm)
    
    slot = graphene.Field("core.queries.SlotType")

    def mutate(self, info, **kwargs):
        if not info.context.user:
            raise GraphQLError(json.dumps({"error": "Not authorized"}))
        kwargs["user"] = info.context.user.id
        form = SlotForm(kwargs)
        if form.is_valid():
            form.save()
            return CreateSlotMutation(slot=form.instance)
        raise GraphQLError(json.dumps(form.errors))



class UpdateSlotMutation(graphene.Mutation):

    Arguments = create_mutation_arguments(SlotForm, edit=True)
    
    slot = graphene.Field("core.queries.SlotType")

    def mutate(self, info, **kwargs):
        if not info.context.user:
            raise GraphQLError(json.dumps({"error": "Not authorized"}))
        kwargs["user"] = info.context.user.id
        slot = info.context.user.slots.filter(id=kwargs["id"])
        if not slot: raise GraphQLError('{"slot": ["Does not exist"]}')
        slot = slot.first()
        form = SlotForm(kwargs, instance=slot)
        if form.is_valid():
            form.save()
            return UpdateSlotMutation(slot=form.instance)
        raise GraphQLError(json.dumps(form.errors))


class MoveSlotMutation(graphene.Mutation):

    class Arguments:
        id = graphene.ID(required=True)
        index = graphene.Int(required=True)
    
    slot = graphene.Field("core.queries.SlotType")
    user = graphene.Field("core.queries.UserType")

    def mutate(self, info, **kwargs):
        if not info.context.user:
            raise GraphQLError(json.dumps({"error": "Not authorized"}))
        slot = info.context.user.slots.filter(id=kwargs["id"])
        if not slot: raise GraphQLError('{"slot": ["Does not exist"]}')
        slot = slot.first()
        slot.move_to(kwargs["index"])
        return MoveSlotMutation(slot=slot, user=slot.user)
        raise GraphQLError(json.dumps(form.errors))



class DeleteSlotMutation(graphene.Mutation):

    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        if not info.context.user:
            raise GraphQLError('{"user": "Not authorized"}')
        slot = info.context.user.slots.filter(id=kwargs["id"])
        if not slot: raise GraphQLError('{"slot": ["Does not exist"]}')
        if slot.first().user.slots.count() == 1:
            raise GraphQLError('{"slot": ["You must have at least one slot"]}')
        slot = slot.first().delete()
        return DeleteSlotMutation(success=True)



class CreateProjectMutation(graphene.Mutation):

    Arguments = create_mutation_arguments(ProjectForm)
    
    project = graphene.Field("core.queries.ProjectType")

    def mutate(self, info, **kwargs):
        if not info.context.user:
            raise GraphQLError(json.dumps({"error": "Not authorized"}))
        kwargs["user"] = info.context.user.id
        form = ProjectForm(kwargs)
        if form.is_valid():
            form.save()
            return CreateProjectMutation(project=form.instance)
        raise GraphQLError(json.dumps(form.errors))



class UpdateProjectMutation(graphene.Mutation):

    Arguments = create_mutation_arguments(ProjectForm, edit=True)
    
    project = graphene.Field("core.queries.ProjectType")

    def mutate(self, info, **kwargs):
        if not info.context.user:
            raise GraphQLError(json.dumps({"error": "Not authorized"}))
        kwargs["user"] = info.context.user.id
        project = info.context.user.projects.filter(id=kwargs["id"])
        if not project: raise GraphQLError('{"project": ["Does not exist"]}')
        project = project.first()
        form = ProjectForm(kwargs, instance=project)
        if form.is_valid():
            form.save()
            return UpdateProjectMutation(project=form.instance)
        raise GraphQLError(json.dumps(form.errors))



class DeleteProjectMutation(graphene.Mutation):

    class Arguments:
        id = graphene.ID(required=True)
    
    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        if not info.context.user:
            raise GraphQLError('{"user": "Not authorized"}')
        project = info.context.user.projects.filter(id=kwargs["id"])
        if not project: raise GraphQLError('{"project": ["Does not exist"]}')
        project = project.first().delete()
        return DeleteProjectMutation(success=True)