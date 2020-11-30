import graphene
from datetime import date
from graphql import GraphQLError
from graphene.relay import Connection, ConnectionField
from graphene_django.types import DjangoObjectType
from core.models import *

class SlotType(DjangoObjectType):

    class Meta:
        model = Slot
    
    operations = graphene.List(
        "core.schema.OperationType",
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



class ProjectType(DjangoObjectType):

    class Meta:
        model = Project
    
    last_activity = graphene.String()



class TaskType(DjangoObjectType):

    class Meta:
        model = Task



class Query(graphene.ObjectType):
    """The root query object. It supplies the user attribute, which is the
    portal through which other attributes are accessed."""

    slot = graphene.Field(SlotType, id=graphene.ID(required=True))
    slots = graphene.List(SlotType)
    operation = graphene.Field("core.schema.OperationType", id=graphene.ID(required=True))
    project = graphene.Field(ProjectType, id=graphene.ID(required=True))
    projects = graphene.List(
        "core.schema.ProjectType"
    )

    def resolve_operation(self, info, **kwargs):
        return Operation.objects.get(id=kwargs["id"])


    def resolve_slot(self, info, **kwargs):
        return Slot.objects.get(id=kwargs["id"])
    

    def resolve_slots(self, info, **kwargs):
        return Slot.objects.all()
    

    def resolve_project(self, info, **kwargs):
        return Project.objects.get(id=kwargs["id"])
    

    def resolve_projects(self, info, **kwargs):
        return Project.objects.all()



class CreateOperationMutation(graphene.Mutation):

    class Arguments:
        name = graphene.String(required=True)
        slot = graphene.ID(required=True)

    operation = graphene.Field(OperationType)

    def mutate(self, info, **kwargs):
        slot = Slot.objects.get(id=kwargs["slot"])
        operation = Operation.objects.create(
            name=kwargs["name"],
            slot=slot,
            slot_order=slot.operations.last().slot_order + 1
        )
        return CreateOperationMutation(operation=operation)



class CompleteOperationMutation(graphene.Mutation):

    class Arguments:
        id = graphene.ID(required=True)

    operation = graphene.Field(OperationType)

    def mutate(self, info, **kwargs):
        operation = Operation.objects.get(id=kwargs["id"])
        operation.completed = date.today()
        operation.save()
        operation.slot.operation = None
        operation.slot.save()
        operation.slot.clean_orders()
        return CompleteOperationMutation(operation=operation)



class ActivateOperationMutation(graphene.Mutation):

    class Arguments:
        id = graphene.ID(required=True)

    operation = graphene.Field(OperationType)

    def mutate(self, info, **kwargs):
        operation = Operation.objects.get(id=kwargs["id"])
        operation.started = date.today()
        operation.save()
        operation.slot.operation = operation
        operation.slot.save()
        operation.slot.clean_orders()
        return ActivateOperationMutation(operation=operation)



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



class CreateTaskMutation(graphene.Mutation):

    class Arguments:
        name = graphene.String(required=True)
        operation = graphene.ID(required=True)

    task = graphene.Field(TaskType)

    def mutate(self, info, **kwargs):
        operation = Operation.objects.get(id=kwargs["operation"])
        task = Task.objects.create(
            name=kwargs["name"],
            operation=operation,
            order=operation.tasks.count() + 1
        )
        return CreateTaskMutation(task=task)



class ToggleTaskMutation(graphene.Mutation):

    class Arguments:
        id = graphene.ID(required=True)

    task = graphene.Field(TaskType)

    def mutate(self, info, **kwargs):
        task = Task.objects.get(id=kwargs["id"])
        task.completed = not task.completed
        task.save()
        return ToggleTaskMutation(task=task)



class DeleteTaskMutation(graphene.Mutation):

    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, **kwargs):
        task = Task.objects.get(id=kwargs["id"])
        task.delete()
        return DeleteTaskMutation(success=True)



class Mutation(graphene.ObjectType):
    create_operation = CreateOperationMutation.Field()
    complete_operation = CompleteOperationMutation.Field()
    activate_operation = ActivateOperationMutation.Field()
    reorder_operations = ReorderOperationsMutation.Field()
    create_task = CreateTaskMutation.Field()
    toggle_task = ToggleTaskMutation.Field()
    delete_task = DeleteTaskMutation.Field()



schema = graphene.Schema(query=Query, mutation=Mutation)