import graphene
from graphene.relay import ConnectionField
from core.forms import *
from core.queries import GoalCategoryType, GoalType, get_filter_arguments

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



class MoveGoal(graphene.Mutation):
    """Moves a goal to a new index."""

    class Arguments:
        goal = graphene.String(required=True)
        index = graphene.Int(required=True)
    
    goals = ConnectionField(
        "core.queries.GoalConnection", **get_filter_arguments(Goal)
    )

    def mutate(self, info, **kwargs):
        import time
        time.sleep(2)
        goal = info.context.user.goals.get(id=kwargs["goal"])
        goal.move_to_index(kwargs["index"])
        return MoveGoal(goals=goal.category.goals.all())



class DeleteGoal(graphene.Mutation):
    """Deletes a goal."""

    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        return delete(info.context.user, Goal, kwargs, DeleteGoal)