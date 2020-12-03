import time
from django.db import models, transaction
from django_random_id_model import RandomIDModel

class Operation(RandomIDModel):

    class Meta:
        db_table = "operations"
        ordering = ["slot_order"]

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    slot_order = models.IntegerField(null=True)
    started = models.DateField(null=True)
    completed = models.DateField(null=True)
    slot = models.ForeignKey("core.Slot", on_delete=models.CASCADE, related_name="operations")


    def __str__(self):
        return self.name
    


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
    completed = models.IntegerField(null=True, default=None)
    order = models.IntegerField()
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE, related_name="tasks")

    def __str__(self):
        return self.name
    

    def save(self, *args, **kwargs):
        """If no order is given, count the number of tasks in the containing
        operation and add one."""
        
        if self.order is None:
            self.order = self.operation.tasks.count() + 1
        super(Task, self).save(*args, **kwargs)
    

    def toggle(self):
        """If not completed, the completed attribute will be set to the current
        time, otherwise it will be set to None."""
        
        self.completed = int(time.time()) if self.completed is None else None
        self.save()
    

    def move(self, index):
        """Moves a task within the containing operation to a new position."""

        if self.order == index + 1: return
        tasks = list(self.operation.tasks.all())
        for task in tasks:
            if task.id == self.id:
                tasks.remove(task)
                tasks.insert(index, self)
                for index, task_ in enumerate(tasks, start=1):
                    task_.order = index
                Task.objects.bulk_update(tasks, ["order"])
                break