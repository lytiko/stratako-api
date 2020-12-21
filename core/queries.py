import graphene
from graphene_django.types import DjangoObjectType
from .models import *

class UserType(DjangoObjectType):
    
    class Meta:
        model = User
        exclude_fields = ["password"]
    
    id = graphene.ID()