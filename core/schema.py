import graphene
from graphql import GraphQLError

class Query(graphene.ObjectType):
    """The root query object. It supplies the user attribute, which is the
    portal through which other attributes are accessed."""

    time = graphene.Int()


schema = graphene.Schema(query=Query)