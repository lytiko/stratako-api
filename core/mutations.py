import graphene
from core.forms import *

def delete(user, Model, data, Mutation):
    """Deletes an object and returns the relevant GraphQL object."""

    instance = getattr(
        user, Model._meta.verbose_name_plural.replace(" ", "_")
    ).get(id=data["id"])
    instance.delete()
    return Mutation(success=True)



class DeleteGoalCategory(graphene.Mutation):
    """Deletes a goal category."""

    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        return delete(info.context.user, GoalCategory, kwargs, DeleteGoalCategory)



class DeleteGoal(graphene.Mutation):
    """Deletes a goal."""

    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        return delete(info.context.user, Goal, kwargs, DeleteGoal)