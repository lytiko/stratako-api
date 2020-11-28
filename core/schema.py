import graphene
from graphql import GraphQLError
from graphene.relay import Connection, ConnectionField
from graphene_django.types import DjangoObjectType
from core.models import Operation

class OperationType(DjangoObjectType):

    class Meta:
        model = Operation



class OperationConnection(Connection):

    class Meta:
        node = OperationType



class Query(graphene.ObjectType):
    """The root query object. It supplies the user attribute, which is the
    portal through which other attributes are accessed."""

    operations = ConnectionField(
        OperationConnection,
        started=graphene.Boolean(), completed=graphene.Boolean(),
        slot=graphene.Int()
    )

    def resolve_operations(self, info, **kwargs):
        operations = Operation.objects.all()
        started, completed = kwargs.get("started"), kwargs.get("completed")
        if started is not None and started:
            operations = operations.exclude(started=None)
        if started is not None and not started:
            operations = operations.filter(started=None)
        if completed is not None and completed:
            operations = operations.exclude(completed=None)
        if completed is not None and not completed:
            operations = operations.filter(completed=None)
        if "slot" in kwargs:
            operations = operations.filter(slot=kwargs["slot"])
        return operations


schema = graphene.Schema(query=Query)