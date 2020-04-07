import graphene
from graphene_django.types import DjangoObjectType
from graphene.relay import Connection, ConnectionField
from .models import User, Goal
from .schema import Datetime

def get_filter_arguments(Model):
    """In GraphQL, fields representing a set of database objects need arguments
    for specifying how those objects should be filtered/sorted. This function
    automatically generates a dict of those arguments from a model's fields."""

    arguments = {}
    for field in Model._meta.fields:
        field_type = field.get_internal_type()
        if field_type == "BooleanField":
            arguments[field.name] = graphene.Boolean()
        if field_type == "CharField" or field_type == "TextField":
            arguments[field.name] = graphene.String()
            arguments[f"{field.name}_contains"] = graphene.String()
        if field_type in ["FloatField", "DateField", "DateTimeField",
         "DecimalField", "IntegerField"]:
            Field = {
                "DateField": graphene.String, "DateTimeField": graphene.Float,
                "IntegerField": graphene.Int
            }.get(field_type, graphene.Float)
            arguments[field.name] = Field()
            arguments[f"{field.name}_gt"] = Field()
            arguments[f"{field.name}_gte"] = Field()
            arguments[f"{field.name}_lt"] = Field()
            arguments[f"{field.name}_lte"] = Field()
        if field_type == "IntegerField":
            arguments[field.name] = graphene.Int()
    arguments["sort"] = graphene.String()
    arguments["tag"] = graphene.String()
    return arguments


def get_objects(queryset, kwargs):
    """Takes a Django queryset and some arguments from a GraphQL query, and
    filters the queryset accordingly. It also sorts and slices as required."""

    special = ["sort", "first", "last", "after", "before"]
    sort, first, last, after, before = [kwargs.get(k) for k in special]
    processed_kwargs = {}
    for key, value in kwargs.items():
        if key in special: continue
        key = "tags__name" if key == "tag" else key
        for suffix in ["gt", "lt", "contains"]:
            key = key.replace(f"_{suffix}", f"__{suffix}")
        processed_kwargs[key] = value
    queryset = queryset.filter(**processed_kwargs)
    if sort: queryset = queryset.order_by(sort)
    return queryset



class Countable:
    """A mixin for connection objects with a count field."""

    count = graphene.Int()

    def resolve_count(self, info, **kwargs):
        return self.iterable.count()



class HasGoals:
    """An object type with goals."""

    goal = graphene.Field(
        "core.queries.GoalType", id=graphene.String(required=True)
    )
    goals = ConnectionField(
        "core.queries.GoalConnection", **get_filter_arguments(Goal)
    )

    def resolve_goal(self, info, **kwargs):
        try:
            return self.goals.get(id=int(kwargs["id"]))
        except AttributeError: return self.iterable.goals.get(id=kwargs["id"])
    

    def resolve_goals(self, context, **kwargs):
        try:
            return get_objects(self.goals, kwargs)
        except AttributeError: return get_objects(self.iterable.goals, kwargs)

        


class GoalType(DjangoObjectType):
    """A lytiko Goal."""

    class Meta:
        model = Goal
        exclude_fields = []
    
    id = graphene.ID()



class GoalConnection(Countable, Connection):
    """A list of Goals."""

    class Meta:
        node = GoalType



class UserType(HasGoals, DjangoObjectType):
    """The user object type. Most other objects are accessed via this object."""
    
    class Meta:
        model = User
        exclude_fields = ["password"]
    
    id = graphene.ID()
    date_joined = Datetime()