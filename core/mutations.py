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


def update(user, Form, data, Mutation):
    """Updates an object and returns the relevant GraphQL object."""

    instance = getattr(
        user, Form._meta.model._meta.verbose_name_plural.replace(" ", "_")
    ).get(id=data["id"])
    form = Form(data=data, instance=instance)
    if form.is_valid():
        form.save()
        return Mutation(**{[k for k, v in Mutation.__dict__.items()
         if isinstance(v, graphene.Field)][0]: form.instance})
    else:
        raise GraphQLError(list(form.errors.values())[0][0])



class DeleteGoalCategory(graphene.Mutation):
    """Deletes a goal category."""

    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        return delete(info.context.user, GoalCategory, kwargs, DeleteGoalCategory)



class UpdateGoal(graphene.Mutation):

    class Arguments:
        id = graphene.String(required=True)
        name = graphene.String()
        description = graphene.String()
    
    goal = graphene.Field("core.queries.GoalType")

    def mutate(self, info, **kwargs):
        return update(info.context.user, GoalForm, kwargs, UpdateGoal)


class MoveGoal(graphene.Mutation):
    """Moves a goal to a new index."""

    class Arguments:
        goal = graphene.String(required=True)
        index = graphene.Int(required=True)
        category = graphene.String()
    
    goals = ConnectionField(
        "core.queries.GoalConnection", **get_filter_arguments(Goal)
    )
    goal_categories = ConnectionField(
        "core.queries.GoalCategoryConnection", **get_filter_arguments(GoalCategory)
    )

    def mutate(self, info, **kwargs):
        goal = info.context.user.goals.get(id=kwargs["goal"])
        goal.move(kwargs["index"], kwargs.get("category"))
        return MoveGoal(
            goals=goal.category.goals.all(),
            goal_categories=info.context.user.goal_categories.all()
        )



class DeleteGoal(graphene.Mutation):
    """Deletes a goal."""

    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        return delete(info.context.user, Goal, kwargs, DeleteGoal)