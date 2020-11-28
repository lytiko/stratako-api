import graphene
from graphql import GraphQLError
from graphene.relay import Connection, ConnectionField
from graphene_django.types import DjangoObjectType
from core.models import Operation, Slot

class SlotType(DjangoObjectType):

    class Meta:
        model = Slot
    
    operations = ConnectionField(
        "core.schema.OperationConnection",
        started=graphene.Boolean(), completed=graphene.Boolean(),
    )
    operation = graphene.Field("core.schema.OperationType")

    def resolve_operations(self, info, **kwargs):
        operations = self.operations.all()
        started, completed = kwargs.get("started"), kwargs.get("completed")
        if started is not None and started:
            operations = operations.exclude(started=None)
        if started is not None and not started:
            operations = operations.filter(started=None)
        if completed is not None and completed:
            operations = operations.exclude(completed=None)
        if completed is not None and not completed:
            operations = operations.filter(completed=None)
        return operations



class OperationType(DjangoObjectType):

    class Meta:
        model = Operation



class OperationConnection(Connection):

    class Meta:
        node = OperationType



class Query(graphene.ObjectType):
    """The root query object. It supplies the user attribute, which is the
    portal through which other attributes are accessed."""

    slot = graphene.Field(SlotType, id=graphene.ID(required=True))
    slots = graphene.List(SlotType)

    def resolve_slot(self, info, **kwargs):
        return Slot.objects.get(id=kwargs["id"])
    

    def resolve_slots(self, info, **kwargs):
        return Slot.objects.all()



class ReorderOperationsMutation(graphene.Mutation):

    class Arguments:
        slot = graphene.ID(required=True)
        operation = graphene.ID(required=True)
        index = graphene.Int(required=True)

    slot = graphene.Field(SlotType)

    def mutate(self, info, **kwargs):
        slot = Slot.objects.get(id=kwargs["slot"])
        operation = Operation.objects.get(id=kwargs["operation"])
        slot.move_operation(operation, kwargs["index"])
        return ReorderOperationsMutation(slot=slot)


class Mutation(graphene.ObjectType):
    reorder_operations = ReorderOperationsMutation.Field()



schema = graphene.Schema(query=Query, mutation=Mutation)