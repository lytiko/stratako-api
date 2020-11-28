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