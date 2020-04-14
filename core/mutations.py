import graphene
from core.forms import *
from core.queries import GoalCategoryType, GoalType

def delete(user, Model, data, Mutation):
    """Deletes an object and returns the relevant GraphQL object."""

    instance = getattr(
        user, Model._meta.verbose_name_plural.replace(" ", "_")
    ).get(id=data["id"])
    instance.delete()
    return Mutation(success=True)



class SwapGoalCategories(graphene.Mutation):
    """Swaps two goal categories."""

    class Arguments:
        category1 = graphene.String(required=True)
        category2 = graphene.String(required=True)
    
    category1 = graphene.Field(GoalCategoryType)
    category2 = graphene.Field(GoalCategoryType)

    def mutate(self, info, **kwargs):
        category1 = info.context.user.goal_categories.get(id=kwargs["category1"])
        category2 = info.context.user.goal_categories.get(id=kwargs["category2"])
        category1.swap_with(category2)
        return SwapGoalCategories(category1=category1, category2=category2)




class DeleteGoalCategory(graphene.Mutation):
    """Deletes a goal category."""

    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        return delete(info.context.user, GoalCategory, kwargs, DeleteGoalCategory)



class SwapGoals(graphene.Mutation):
    """Swaps two goals."""

    class Arguments:
        goal1 = graphene.String(required=True)
        goal2 = graphene.String(required=True)
    
    goal1 = graphene.Field(GoalType)
    goal2 = graphene.Field(GoalType)

    def mutate(self, info, **kwargs):
        goal1 = info.context.user.goals.get(id=kwargs["goal1"])
        goal2 = info.context.user.goals.get(id=kwargs["goal2"])
        goal1.swap_with(goal2)
        return SwapGoals(goal1=goal1, goal2=goal2)



class DeleteGoal(graphene.Mutation):
    """Deletes a goal."""

    class Arguments:
        id = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        return delete(info.context.user, Goal, kwargs, DeleteGoal)