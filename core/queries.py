import graphene
from graphene_django.types import DjangoObjectType
from graphene.relay import ConnectionField
from .models import User
from .schema import Datetime

class UserType(DjangoObjectType):
    """The user object type. Most other objects are accessed via this object."""
    
    class Meta:
        model = User
        exclude_fields = ["password"]
    
    id = graphene.ID()
    date_joined = Datetime()