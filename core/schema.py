import graphene
from datetime import date
from graphql import GraphQLError
from graphene.relay import Connection, ConnectionField
from graphene_django.types import DjangoObjectType
from django.db import transaction

class Query(graphene.ObjectType):

    time = graphene.Int()

schema = graphene.Schema(query=Query)