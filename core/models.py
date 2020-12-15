import time
from datetime import date
from django_random_id_model import RandomIDModel
from django.db import models, transaction
from django.core.exceptions import ValidationError

class Operation(RandomIDModel):

    class Meta:
        db_table = "operations"
        ordering = ["order", "started"]

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    order = models.IntegerField(null=True)
    started = models.DateField(null=True, default=None)
    completed = models.DateField(null=True, default=None)
    slot = models.ForeignKey("core.Slot", on_delete=models.CASCADE, related_name="operations")


    def __str__(self):
        return self.name
    

    def save(self, *args, **kwargs):
        """If no order is given, count the number of tasks in the containing
        slot and add one."""
        
        if self.order is None and not self.started:
            self.order = self.slot.operations.filter(started=None).count() + 1
        if self.started: self.order = None
        super(Operation, self).save(*args, **kwargs)
    

    def move(self, index, slot=None):
        """Moves an operation within the containing slot to a new position, or
        to a position with another slot."""

        destination = slot or self.slot
        source_operations = list(self.slot.operations.filter(started=None))
        dest_operations = list(destination.operations.filter(started=None)) if \
            self.slot is not destination else source_operations
        for operation in source_operations:
            if operation.id == self.id:
                self.slot = destination
                if slot: self.save()
                source_operations.remove(operation)
                dest_operations.insert(index, self)
                for index, operation_ in enumerate(source_operations, start=1):
                    operation_.order = index
                for index, operation_ in enumerate(dest_operations, start=1):
                    operation_.order = index
                Operation.objects.bulk_update(
                    source_operations + dest_operations, ["order"]
                )
                break
    


class Slot(RandomIDModel):

    class Meta:
        db_table = "slots"
        ordering = ["order"]
    
    name = models.CharField(max_length=50)
    order = models.IntegerField()
    operation = models.OneToOneField(
        Operation, on_delete=models.CASCADE,
        related_name="slot_active", null=True
    )

    def __str__(self):
        return f"{self.order}: {self.name}"


    def clean_orders(self):
        completed = list(self.operations.exclude(completed=None))
        current = list(self.operations.filter(completed=None).exclude(started=None))
        future = list(self.operations.filter(completed=None, started=None))
        completed.sort(key=lambda o: o.completed)
        future.sort(key=lambda o: o.slot_order)
        for index, operation in enumerate(completed + current + future):
            operation.slot_order = index + 1
            operation.save()

    
    def move_operation(self, operation, index):
        operations = list(self.operations.filter(started=None))
        start_index = operations[0].slot_order
        for op_index, op in enumerate(operations):
            if op.id == operation.id:
                operations.remove(op)
                operations.insert(index  if op_index > index else index, op)
                for index2, op2 in enumerate(operations):
                    op2.slot_order = index2 + start_index
                    op2.save()
                return



class Project(RandomIDModel):

    class Meta:
        db_table = "projects"
    
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    color = models.CharField(max_length=20, default="")
    operations = models.ManyToManyField(Operation, through="core.ProjectOperationLink", related_name="projects")

    def __str__(self):
        return self.name
    

    @property
    def last_activity(self):
        active = self.operations.filter(completed=None).exclude(started=None)
        if active.count(): return active.last().started
        completed = self.operations.exclude(completed=None)
        if completed.count(): return completed.last().completed
        return None



class ProjectOperationLink(RandomIDModel):

    class Meta:
        db_table = "project_operation_links"
    
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    project_order = models.IntegerField()



class Task(RandomIDModel):

    class Meta:
        db_table = "tasks"
        ordering = ["order"]

    name = models.CharField(max_length=50)
    completed = models.IntegerField(null=True, blank=True, default=None)
    order = models.IntegerField()
    operation = models.ForeignKey(
        Operation, on_delete=models.CASCADE,
        related_name="tasks", null=True, blank=True
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE,
        related_name="tasks", null=True, blank=True
    )

    def __str__(self):
        return self.name
    

    def save(self, *args, **kwargs):
        """If no order is given, count the number of tasks in the containing
        operation and add one."""
        
        if self.project is None and self.operation is None:
            raise ValidationError("Need a project or operation")
        if self.project is not None and self.operation is not None:
            raise ValidationError("Can't have project and operation")
        if self.order is None:
            container = self.operation or self.project
            self.order = container.tasks.count() + 1
        super(Task, self).save(*args, **kwargs)
    

    def toggle(self):
        """If not completed, the completed attribute will be set to the current
        time, otherwise it will be set to None."""
        
        self.completed = int(time.time()) if self.completed is None else None
        self.save()
    

    def move(self, index, operation=None, project=None):
        """Moves a task within the containing operation/project to a new
        position, or to a position with another operation/project."""

        source_container = self.operation or self.project
        destination_container = operation or project or source_container
        source_tasks = list(source_container.tasks.all())
        dest_tasks = list(destination_container.tasks.all()) if \
            source_container is not destination_container else source_tasks
        for task in source_tasks:
            if task.id == self.id:
                if operation:
                    self.operation = operation
                    if self.project: self.project = None
                if project:
                    self.project = project
                    if self.operation: self.operation = None
                if operation or project: self.save()
                source_tasks.remove(task)
                dest_tasks.insert(index, self)
                for index, task_ in enumerate(source_tasks, start=1):
                    task_.order = index
                for index, task_ in enumerate(dest_tasks, start=1):
                    task_.order = index
                Task.objects.bulk_update(source_tasks + dest_tasks, ["order"])
                break