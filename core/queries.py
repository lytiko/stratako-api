import graphene
from graphene_django.types import DjangoObjectType
from .models import *

class UserType(DjangoObjectType):
    
    class Meta:
        model = User
        exclude_fields = ["password"]
    
    id = graphene.ID()
    slots = graphene.List("core.queries.SlotType")

    def resolve_slots(self, info, **kwargs):
        return self.slots.all()



class SlotType(DjangoObjectType):
    
    class Meta:
        model = Slot
    
    id = graphene.ID()