from django.db import models 

class Operation(models.Model):

    class Meta:
        db_table = "operations"
        ordering = ["-started", "slot_order"]

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    slot = models.IntegerField(null=True)
    slot_order = models.IntegerField(null=True)
    started = models.DateField(null=True)
    completed = models.DateField(null=True)

    def __str__(self):
        return self.name
    

    def move_to_index(self, index):
        operations = list(Operation.objects.filter(slot=self.slot).exclude(slot_order=None))
        operations.insert(index if index < self.slot_order else index + 1, self)
        operations = [o for o in operations if o.id != self.id or o is self]
        for index, operation in enumerate(operations):
            operation.slot_order = index
            operation.save()