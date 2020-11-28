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



class ReorderOperationMutation(graphene.Mutation):

    class Arguments:
        slot = graphene.Int(required=True)
        operation = graphene.ID(required=True)
        index = graphene.Int(required=True)

    operations = ConnectionField("core.schema.OperationConnection")

    def mutate(self, info, **kwargs):
        operation = Operation.objects.get(id=kwargs["operation"])
        operation.move_to_index(kwargs["index"])
        return ReorderOperationMutation(operations=Operation.objects.filter(
            slot=operation.slot, completed=None, started=None
        ))


class Mutation(graphene.ObjectType):
    reorder_operation = ReorderOperationMutation.Field()



schema = graphene.Schema(query=Query, mutation=Mutation)