import graphene
from datetime import date
from graphql import GraphQLError
from graphene.relay import Connection, ConnectionField
from graphene_django.types import DjangoObjectType
from django.db import transaction
from core.models import *

class SlotType(DjangoObjectType):

    class Meta:
        model = Slot
    
    id = graphene.String()
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
    
    id = graphene.String()



class ProjectType(DjangoObjectType):

    class Meta:
        model = Project
    
    id = graphene.String()
    last_activity = graphene.String()



class TaskType(DjangoObjectType):

    class Meta:
        model = Task
    
    id = graphene.String()



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
            order=slot.operations.last().order + 1
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



class UpdateOperationMutation(graphene.Mutation):

    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        description = graphene.String()

    operation = graphene.Field(OperationType)

    def mutate(self, info, **kwargs):
        operation = Operation.objects.get(id=kwargs["id"])
        operation.name = kwargs["name"]
        operation.description = kwargs.get("description", "")
        operation.save()
        return UpdateOperationMutation(operation=operation)



class UpdateOperationProjectsMutation(graphene.Mutation):

    class Arguments:
        id = graphene.ID(required=True)
        projects = graphene.List(graphene.ID, required=True)

    operation = graphene.Field(OperationType)

    def mutate(self, info, **kwargs):
        operation = Operation.objects.get(id=kwargs["id"])
        with transaction.atomic():
            for project in operation.projects.all():
                operation.projects.remove(project)
            for index, id in enumerate(kwargs["projects"]):
                project = Project.objects.get(id=id)
                ProjectOperationLink.objects.create(
                    operation=operation,
                    project=project,
                    project_order=project.operations.count() + 1
                )
        operation.save()
        return UpdateOperationProjectsMutation(operation=operation)



class CreateTaskMutation(graphene.Mutation):

    class Arguments:
        name = graphene.String(required=True)
        operation = graphene.ID()
        project = graphene.ID()

    task = graphene.Field(TaskType)

    def mutate(self, info, **kwargs):
        operation, project = kwargs.get("operation"), kwargs.get("project")
        if operation: operation = Operation.objects.get(id=kwargs.get("operation"))
        if project: project = Project.objects.get(id=kwargs.get("project"))
        task = Task.objects.create(name=kwargs["name"], operation=operation, project=project)
        return CreateTaskMutation(task=task)



class UpdateTaskMutation(graphene.Mutation):

    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)

    task = graphene.Field(TaskType)

    def mutate(self, info, **kwargs):
        task = Task.objects.get(id=kwargs["id"])
        task.name = kwargs["name"]
        task.save()
        return UpdateTaskMutation(task=task)



class ToggleTaskMutation(graphene.Mutation):

    class Arguments:
        id = graphene.ID(required=True)

    task = graphene.Field(TaskType)

    def mutate(self, info, **kwargs):
        task = Task.objects.get(id=kwargs["id"])
        task.toggle()
        return ToggleTaskMutation(task=task)



class MoveTaskMutation(graphene.Mutation):

    class Arguments:
        id = graphene.ID(required=True)
        index = graphene.Int(required=True)
        operation = graphene.ID(required=False)
        project = graphene.ID(required=False)

    task = graphene.Field(TaskType)

    def mutate(self, info, **kwargs):
        task = Task.objects.get(id=kwargs["id"])
        operation = Operation.objects.get(id=kwargs["operation"]) if "operation" in kwargs else None
        project = Project.objects.get(id=kwargs["project"]) if "project" in kwargs else None
        task.move(kwargs["index"], operation=operation, project=project)
        return MoveTaskMutation(task=task)



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
    update_operation = UpdateOperationMutation.Field()
    update_operation_projects = UpdateOperationProjectsMutation.Field()
    complete_operation = CompleteOperationMutation.Field()
    activate_operation = ActivateOperationMutation.Field()
    reorder_operations = ReorderOperationsMutation.Field()
    create_task = CreateTaskMutation.Field()
    update_task = UpdateTaskMutation.Field()
    toggle_task = ToggleTaskMutation.Field()
    move_task = MoveTaskMutation.Field()
    delete_task = DeleteTaskMutation.Field()



schema = graphene.Schema(query=Query, mutation=Mutation)