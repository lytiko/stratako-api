import graphene
from graphene_django.types import DjangoObjectType
from core.models import User

class UserType(DjangoObjectType):
    """The user object type. Most other objects are accessed via this object.
    """
    
    class Meta:
        model = User
        exclude_fields = ["password"]
    
    id = graphene.ID()