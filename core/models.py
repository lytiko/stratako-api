from django.db import models 

class Operation(models.Model):

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
    


class Slot(models.Model):

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


