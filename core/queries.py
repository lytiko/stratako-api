import graphene
from graphene_django.types import DjangoObjectType
from graphql import GraphQLError
from .models import *

class UserType(DjangoObjectType):
    
    class Meta:
        model = User
        exclude_fields = ["password"]
    
    id = graphene.ID()
    slots = graphene.List("core.queries.SlotType")
    project = graphene.Field("core.queries.ProjectType", id=graphene.ID(required=True))
    projects = graphene.List("core.queries.ProjectType")

    def resolve_slots(self, info, **kwargs):
        return self.slots.all()

    
    def resolve_project(self, info, **kwargs):
        project = self.projects.filter(id=int(kwargs["id"])).first()
        if project: return project
        raise GraphQLError('{"project": "Does not exist"}')


    def resolve_projects(self, info, **kwargs):
        return self.projects.all()



class SlotType(DjangoObjectType):
    
    class Meta:
        model = Slot
    
    id = graphene.ID()



class ProjectType(DjangoObjectType):
    
    class Meta:
        model = Project
    
    id = graphene.ID()
    status = graphene.Int()